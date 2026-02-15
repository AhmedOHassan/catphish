"""
Catphish API Backend — serves both the B2B tenant API and the
session-based endpoints consumed by the React verification frontend.
"""

from __future__ import annotations

import json
import os
import secrets
import time
from typing import Optional, Literal, List, Any

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path

import logging

from db.valkey_store import ValkeyStore, Tenant
from voice.encoder import create_embedding
from voice.verification import compare_embeddings
from voice.comprehension import comprehension_check
from voice.phrase_generator import generate_verification_phrase, generate_enrollment_phrases, get_enrollment_phrase
from voice.audio_utils import base64_to_bytes
from solana_audit import log_verification_attempt

load_dotenv()

# ── Logging setup ──
logging.basicConfig(
    level=logging.DEBUG,
    format="\n🐟 %(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("catphish")
log.setLevel(logging.DEBUG)

APP_NAME = "catphish-api"
API_VERSION = "v1"

# ---- config ----
VALKEY_HOST = os.getenv("VALKEY_HOST", "127.0.0.1")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "6379"))
DEFAULT_TTL_SECONDS = int(os.getenv("CHALLENGE_TTL_SECONDS", "120"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))

log.info("="*60)
log.info("  CATPHISH API STARTING UP")
log.info(f"  Valkey: {VALKEY_HOST}:{VALKEY_PORT}")
log.info(f"  Challenge TTL: {DEFAULT_TTL_SECONDS}s | Rate limit: {RATE_LIMIT_PER_MINUTE}/min")
log.info("="*60)

store = ValkeyStore(host=VALKEY_HOST, port=VALKEY_PORT)

try:
    pong = store.r.ping()
    log.info(f"✅ Valkey connection: {'OK' if pong else 'FAILED'}")
except Exception as e:
    log.error(f"❌ Valkey connection FAILED: {e}")

app = FastAPI(title=APP_NAME, version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# Pydantic Models
# =====================================================================

# --- B2B Tenant API Models ---
class EnrollmentRequest(BaseModel):
    external_user_id: str = Field(..., min_length=1, max_length=200)
    audio_sample: str = Field(..., description="base64 encoded audio for MVP demo")
    metadata: Optional[dict] = None


class EnrollmentResponse(BaseModel):
    tenant_id: str
    external_user_id: str
    enrolled: bool
    embedding_version: str
    created_at: str


class CreateChallengeRequest(BaseModel):
    external_user_id: str = Field(..., min_length=1, max_length=200)
    purpose: Optional[str] = Field(default="login")
    ttl_seconds: Optional[int] = Field(default=DEFAULT_TTL_SECONDS, ge=30, le=180)


class CreateChallengeResponse(BaseModel):
    challenge_id: str
    external_user_id: str
    phrase: str
    expires_in_seconds: int
    challenge_url: str


VerifyStatus = Literal["verified", "failed", "expired", "replay_blocked", "rate_limited"]


class VerifyChallengeRequest(BaseModel):
    external_user_id: str = Field(..., min_length=1, max_length=200)
    audio_sample: str = Field(..., description="base64 encoded audio")
    client_timestamp: Optional[str] = None


class VerifyChallengeResponse(BaseModel):
    challenge_id: str
    external_user_id: str
    status: VerifyStatus
    confidence_score: float
    risk_level: Literal["low", "medium", "high"]
    reasons: List[str]
    similarity: Optional[float] = None


class HealthResponse(BaseModel):
    ok: bool
    valkey: str
    timestamp: int


class CreateVerificationSessionRequest(BaseModel):
    external_user_id: str = Field(..., min_length=1, max_length=200)
    return_url: Optional[str] = None


class CreateVerificationSessionResponse(BaseModel):
    session_id: str
    verification_url: str


class GetVerificationSessionResponse(BaseModel):
    session_id: str
    external_user_id: str
    return_url: Optional[str]


# --- Frontend / Session-based Models ---
class SessionStatusResponse(BaseModel):
    session_id: str
    external_user_id: str
    return_url: Optional[str]
    enrolled: bool
    phrase: str
    instruction: Optional[str] = None
    expected_behavior: Optional[str] = None
    phrase_type: Optional[str] = None  # 'enrollment' | 'verification'


class SessionEnrollRequest(BaseModel):
    audio_sample: str = Field(..., description="base64 encoded audio")


class SessionEnrollResponse(BaseModel):
    success: bool
    message: str
    enrolled: bool


class SessionVerifyRequest(BaseModel):
    audio_sample: str = Field(..., description="base64 encoded audio")


class SessionVerifyResponse(BaseModel):
    status: str  # "verified" | "failed" | "error"
    message: str
    confidence_score: Optional[float] = None
    similarity: Optional[float] = None
    comprehension: Optional[dict] = None
    reasons: Optional[List[str]] = None
    solana_tx: Optional[dict] = None  # on-chain audit trail


# =====================================================================
# Helpers
# =====================================================================
def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def require_tenant(
    x_catphish_key: Optional[str] = Header(default=None, alias="X-Catphish-Key"),
) -> Tenant:
    log.debug(f"🔑 require_tenant called — key present: {bool(x_catphish_key)}")
    if not x_catphish_key:
        log.warning("🚫 Missing X-Catphish-Key header")
        raise HTTPException(status_code=401, detail="Missing X-Catphish-Key")
    tenant = store.get_tenant_by_api_key(x_catphish_key.strip())
    if not tenant or not tenant.tenant_id:
        log.warning(f"🚫 Invalid API key: {x_catphish_key[:8]}...")
        raise HTTPException(status_code=401, detail="Invalid tenant API key")
    log.info(f"✅ Tenant authenticated: {tenant.tenant_id} ({tenant.name})")
    return tenant


def generate_phrase() -> str:
    """Generate a random tongue-twister-style passphrase."""
    colors = ["Silver", "Purple", "Golden", "Crimson", "Azure", "Emerald"]
    animals = ["tiger", "rocket", "dragon", "phoenix", "falcon", "leopard"]
    numbers = [str(n) for n in range(11, 99)]
    verbs = ["jumps", "dances", "moves", "flies", "runs", "spins"]
    adverbs = ["quickly", "loudly", "smoothly", "swiftly", "gracefully", "boldly"]
    return (
        f"{secrets.choice(colors)} {secrets.choice(animals)} "
        f"{secrets.choice(numbers)} {secrets.choice(verbs)} {secrets.choice(adverbs)}"
    )


def parse_embedding(voice_embedding: Any) -> list:
    if isinstance(voice_embedding, str):
        return json.loads(voice_embedding)
    return voice_embedding


# =====================================================================
# Routes — Health
# =====================================================================
@app.get("/health", response_model=HealthResponse)
def health():
    log.info("💓 Health check requested")
    try:
        pong = store.r.ping()
        log.info(f"💓 Valkey ping: {'PONG ✅' if pong else 'FAILED ❌'}")
        return HealthResponse(
            ok=bool(pong),
            valkey=f"{VALKEY_HOST}:{VALKEY_PORT}",
            timestamp=int(time.time()),
        )
    except Exception as e:
        log.error(f"💀 Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Valkey health check failed: {e}")


# =====================================================================
# Routes — B2B Tenant API (requires X-Catphish-Key)
# =====================================================================

@app.post(
    f"/{API_VERSION}/verification-sessions",
    response_model=CreateVerificationSessionResponse,
    status_code=201,
)
def create_verification_session(
    req: CreateVerificationSessionRequest,
    tenant: Tenant = Depends(require_tenant),
):
    log.info("="*50)
    log.info("📋 CREATE VERIFICATION SESSION")
    log.info(f"   tenant:  {tenant.tenant_id}")
    log.info(f"   user:    {req.external_user_id}")
    log.info(f"   return:  {req.return_url}")
    session_id = "vs_" + secrets.token_hex(16)
    store.create_verification_session(
        session_id=session_id,
        tenant_id=tenant.tenant_id,
        external_user_id=req.external_user_id,
        return_url=req.return_url,
        ttl_seconds=600,
    )
    frontend_url = os.getenv("CATPHISH_FRONTEND_URL", "http://localhost:3001")
    verification_url = f"{frontend_url}/verify?session_id={session_id}"
    log.info(f"   ✅ session created: {session_id}")
    log.info(f"   🔗 redirect URL:   {verification_url}")
    log.info("="*50)
    return CreateVerificationSessionResponse(
        session_id=session_id,
        verification_url=verification_url,
    )


@app.get(
    f"/{API_VERSION}/verification-sessions/{{session_id}}",
    response_model=GetVerificationSessionResponse,
)
def get_verification_session(
    session_id: str,
    tenant: Tenant = Depends(require_tenant),
):
    session = store.get_verification_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Verification session not found or expired")
    if session.tenant_id != tenant.tenant_id:
        raise HTTPException(status_code=403, detail="Session belongs to different tenant")
    return GetVerificationSessionResponse(
        session_id=session.session_id,
        external_user_id=session.external_user_id,
        return_url=session.return_url,
    )


@app.post(f"/{API_VERSION}/enroll", response_model=EnrollmentResponse)
def enroll(req: EnrollmentRequest, tenant: Tenant = Depends(require_tenant)):
    try:
        audio_bytes = base64_to_bytes(req.audio_sample)
        embedding = create_embedding(audio_bytes)
        embedding_list = embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process audio: {e}")

    user = store.upsert_user_embedding(
        tenant_id=tenant.tenant_id,
        external_user_id=req.external_user_id,
        voice_embedding=embedding_list,
        created_at_iso=now_iso(),
    )
    return EnrollmentResponse(
        tenant_id=tenant.tenant_id,
        external_user_id=req.external_user_id,
        enrolled=True,
        embedding_version="v1",
        created_at=user.created_at or now_iso(),
    )


@app.post(
    f"/{API_VERSION}/challenges",
    response_model=CreateChallengeResponse,
    status_code=201,
)
def create_challenge(
    req: CreateChallengeRequest,
    tenant: Tenant = Depends(require_tenant),
):
    user = store.get_user(tenant.tenant_id, req.external_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not enrolled")

    challenge_id = "ch_" + secrets.token_hex(4)
    phrase = generate_phrase()
    ttl = int(req.ttl_seconds or DEFAULT_TTL_SECONDS)
    store.create_challenge(
        tenant_id=tenant.tenant_id,
        challenge_id=challenge_id,
        external_user_id=req.external_user_id,
        phrase=phrase,
        ttl_seconds=ttl,
    )
    base_url = os.getenv("PUBLIC_BASE_URL", "https://catphish.tech")
    challenge_url = f"{base_url}/challenge/{challenge_id}"
    return CreateChallengeResponse(
        challenge_id=challenge_id,
        external_user_id=req.external_user_id,
        phrase=phrase,
        expires_in_seconds=ttl,
        challenge_url=challenge_url,
    )


@app.post(
    f"/{API_VERSION}/challenges/{{challenge_id}}/verify",
    response_model=VerifyChallengeResponse,
)
def verify_challenge(
    challenge_id: str,
    req: VerifyChallengeRequest,
    tenant: Tenant = Depends(require_tenant),
):
    # Rate limit
    allowed, count, ttl = store.check_rate_limit(
        tenant_id=tenant.tenant_id,
        external_user_id=req.external_user_id,
        limit=RATE_LIMIT_PER_MINUTE,
        window_seconds=60,
    )
    if not allowed:
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="rate_limited",
            confidence_score=0.0,
            risk_level="high",
            reasons=[f"rate_limited count={count} ttl={ttl}"],
        )

    # Anti-replay
    if not store.claim_challenge_lock(tenant.tenant_id, challenge_id):
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="replay_blocked",
            confidence_score=0.0,
            risk_level="high",
            reasons=["challenge_lock_exists_replay_blocked"],
        )

    ch = store.get_challenge(tenant.tenant_id, challenge_id)
    if not ch:
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="expired",
            confidence_score=0.0,
            risk_level="high",
            reasons=["challenge_missing_or_expired"],
        )

    if ch.external_user_id != req.external_user_id:
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="failed",
            confidence_score=0.0,
            risk_level="high",
            reasons=["external_user_id_mismatch"],
        )

    user = store.get_user(tenant.tenant_id, req.external_user_id)
    if not user or not user.voice_embedding:
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="failed",
            confidence_score=0.0,
            risk_level="high",
            reasons=["user_not_enrolled"],
        )

    # Real verification pipeline
    try:
        audio_bytes = base64_to_bytes(req.audio_sample)
        test_embedding = create_embedding(audio_bytes)
        enrolled_embedding = parse_embedding(user.voice_embedding)

        # Layer 1 — speaker similarity
        layer1_result = compare_embeddings(enrolled_embedding, test_embedding)

        # Layer 2 — comprehension check (if phrase exists)
        layer2_result = None
        if ch.phrase:
            challenge = generate_verification_phrase()
            layer2_result = comprehension_check(
                audio_data=audio_bytes,
                instruction=challenge['instruction'],
                expected_behavior=challenge['expected_behavior'],
                similarity_score=layer1_result["similarity"],
            )

        reasons: list[str] = []
        failed = False

        if not layer1_result["match"]:
            failed = True
            reasons.append(f"speaker_mismatch (similarity: {layer1_result['similarity']:.2f})")
        if layer2_result and not layer2_result.get("skipped"):
            if layer2_result.get("recommendation") == "BLOCK":
                failed = True
                reasons.append(f"comprehension_failed: {layer2_result.get('reasoning', 'Unknown')}")
            elif layer2_result.get("recommendation") == "CHALLENGE_AGAIN":
                failed = True
                reasons.append(f"challenge_again: {layer2_result.get('reasoning', 'Unknown')}")

        overall_confidence = layer1_result["confidence"]
        if (
            layer2_result
            and not layer2_result.get("skipped")
            and layer2_result.get("confidence") is not None
        ):
            overall_confidence = (overall_confidence + float(layer2_result["confidence"])) / 2.0

        if failed:
            status: VerifyStatus = "failed"
            risk = "high"
            if not reasons:
                reasons = ["verification_failed"]
        else:
            status = "verified"
            risk = "low"
            reasons = ["all_layers_passed"]

    except Exception as e:
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="failed",
            confidence_score=0.0,
            risk_level="high",
            reasons=[f"verification_error: {e!s}"],
        )

    store.set_challenge_status(tenant.tenant_id, challenge_id, status)

    return VerifyChallengeResponse(
        challenge_id=challenge_id,
        external_user_id=req.external_user_id,
        status=status,
        confidence_score=overall_confidence,
        risk_level=risk,
        reasons=reasons,
        similarity=layer1_result["similarity"],
    )


# =====================================================================
# Routes — Session-Based Frontend API (no X-Catphish-Key needed)
#
# These endpoints are called directly by the React verification frontend.
# Auth is via the session_id itself (which maps to a tenant + user).
# =====================================================================

def _resolve_session(session_id: str):
    """Look up a verification session and its associated tenant/user."""
    log.debug(f"🔍 Resolving session: {session_id}")
    session = store.get_verification_session(session_id)
    if not session:
        log.warning(f"❌ Session NOT found or expired: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found or expired")
    log.debug(f"   ✅ Session found → tenant={session.tenant_id}, user={session.external_user_id}")
    return session


@app.get(f"/{API_VERSION}/session/{{session_id}}/status", response_model=SessionStatusResponse)
def session_status(session_id: str):
    """
    Frontend calls this on page load to know:
    - Who the user is (external_user_id)
    - Where to redirect after success (return_url)
    - Whether the user already has an enrolled voice
    - A phrase to speak
    """
    log.info("")
    log.info("━"*55)
    log.info("📡 SESSION STATUS — frontend page loaded")
    log.info(f"   session_id: {session_id}")
    session = _resolve_session(session_id)
    user = store.get_user(session.tenant_id, session.external_user_id)
    enrolled = bool(user and user.voice_embedding)

    if enrolled:
        # Verification: single anti-TTS instruction phrase
        challenge = generate_verification_phrase()
        phrase = challenge['instruction']
        instruction = challenge['instruction']
        expected_behavior = challenge['expected_behavior']
        phrase_type = 'verification'
    else:
        # Enrollment: 5 instruction phrases for a richer voice baseline.
        # This gives Resemblyzer more varied speech to build a robust
        # embedding, and uses the same kind of speech as verification.
        challenge = generate_enrollment_phrases(5)
        phrase = challenge['instruction']
        instruction = challenge['instruction']
        expected_behavior = challenge['expected_behavior']
        phrase_type = 'enrollment'

    log.info(f"   external_user_id: {session.external_user_id}")
    log.info(f"   return_url:       {session.return_url}")
    log.info(f"   enrolled:         {'YES ✅ (returning user → verify flow)' if enrolled else 'NO ❌ (new user → enrollment flow)'}")
    if enrolled:
        emb_preview = str(user.voice_embedding)[:80] + "..." if user and user.voice_embedding else "N/A"
        log.info(f"   stored embedding: {emb_preview}")
    # Store the instruction in the session so session_verify uses the SAME phrase
    session_key = store.k_verification_session(session_id)
    store.r.hset(session_key, mapping={
        'challenge_instruction': instruction,
        'challenge_expected_behavior': expected_behavior,
        'challenge_phrase_type': phrase_type,
    })

    log.info(f"   phrase_type:      {phrase_type}")
    log.info(f"   phrase:           \"{phrase}\"")
    log.info("━"*55)
    return SessionStatusResponse(
        session_id=session_id,
        external_user_id=session.external_user_id,
        return_url=session.return_url,
        enrolled=enrolled,
        phrase=phrase,
        instruction=instruction,
        expected_behavior=expected_behavior,
        phrase_type=phrase_type,
    )


@app.post(f"/{API_VERSION}/session/{{session_id}}/enroll", response_model=SessionEnrollResponse)
def session_enroll(session_id: str, req: SessionEnrollRequest):
    """
    First-time user: record voice → create embedding → store it.
    Called by the verification frontend when user is NOT yet enrolled.
    """
    log.info("")
    log.info("🟢" + "="*53)
    log.info("🎤 ENROLLMENT — new user registering voice")
    log.info(f"   session_id: {session_id}")
    session = _resolve_session(session_id)
    log.info(f"   tenant:     {session.tenant_id}")
    log.info(f"   user:       {session.external_user_id}")

    audio_b64_len = len(req.audio_sample) if req.audio_sample else 0
    log.info(f"   audio payload: {audio_b64_len} chars base64 (~{audio_b64_len * 3 // 4 // 1024} KB raw)")

    try:
        log.info("   [Step 1/3] Decoding base64 → raw audio bytes...")
        audio_bytes = base64_to_bytes(req.audio_sample)
        log.info(f"   ✅ Got {len(audio_bytes)} bytes of audio")

        log.info("   [Step 2/3] Creating voice embedding (Resemblyzer)...")
        embedding = create_embedding(audio_bytes)
        embedding_list = embedding.tolist()
        log.info(f"   ✅ Embedding created: dimension={len(embedding_list)}, first 5 values={embedding_list[:5]}")
    except Exception as e:
        log.error(f"   ❌ ENROLLMENT FAILED during audio processing: {e}")
        log.exception(e)
        raise HTTPException(status_code=400, detail=f"Audio processing failed: {e}")

    log.info("   [Step 3/3] Storing embedding in Valkey...")
    store.upsert_user_embedding(
        tenant_id=session.tenant_id,
        external_user_id=session.external_user_id,
        voice_embedding=embedding_list,
        created_at_iso=now_iso(),
    )
    log.info(f"   ✅ Voice profile saved for user {session.external_user_id}")
    log.info("🟢 ENROLLMENT COMPLETE — user is now enrolled")
    log.info("🟢" + "="*53)

    return SessionEnrollResponse(
        success=True,
        message="Voice enrolled successfully. You are now verified.",
        enrolled=True,
    )


@app.post(f"/{API_VERSION}/session/{{session_id}}/verify", response_model=SessionVerifyResponse)
def session_verify(session_id: str, req: SessionVerifyRequest):
    """
    Returning user: record voice → check AI + speaker match.
    Called by the verification frontend when user IS already enrolled.
    """
    log.info("")
    log.info("🔵" + "="*53)
    log.info("🔐 VERIFICATION — returning user verifying voice")
    log.info(f"   session_id: {session_id}")
    session = _resolve_session(session_id)
    log.info(f"   tenant:     {session.tenant_id}")
    log.info(f"   user:       {session.external_user_id}")

    user = store.get_user(session.tenant_id, session.external_user_id)

    if not user or not user.voice_embedding:
        log.warning("   ❌ No voice profile found — user never enrolled!")
        return SessionVerifyResponse(
            status="failed",
            message="No voice profile found. Please enroll first.",
            reasons=["user_not_enrolled"],
        )
    log.info("   ✅ Voice profile found in Valkey")

    # Rate limit
    allowed, count, ttl = store.check_rate_limit(
        tenant_id=session.tenant_id,
        external_user_id=session.external_user_id,
        limit=RATE_LIMIT_PER_MINUTE,
        window_seconds=60,
    )
    log.info(f"   Rate limit: {count}/{RATE_LIMIT_PER_MINUTE} attempts (window TTL: {ttl}s) — {'ALLOWED ✅' if allowed else 'BLOCKED ❌'}")
    if not allowed:
        log.warning(f"   🚫 RATE LIMITED — user exceeded {RATE_LIMIT_PER_MINUTE} attempts")
        return SessionVerifyResponse(
            status="failed",
            message=f"Too many attempts. Try again in {ttl} seconds.",
            reasons=["rate_limited"],
        )

    audio_b64_len = len(req.audio_sample) if req.audio_sample else 0
    log.info(f"   audio payload: {audio_b64_len} chars base64 (~{audio_b64_len * 3 // 4 // 1024} KB raw)")

    try:
        log.info("   ──────────────────────────────────────")
        log.info("   [Step 1/3] Decoding base64 → raw audio bytes...")
        audio_bytes = base64_to_bytes(req.audio_sample)
        log.info(f"   ✅ Got {len(audio_bytes)} bytes of audio")

        log.info("   [Step 2/3] Creating embedding from test audio (Resemblyzer)...")
        test_embedding = create_embedding(audio_bytes)
        log.info(f"   ✅ Test embedding: dim={len(test_embedding)}, first 3={test_embedding[:3].tolist()}")

        enrolled_embedding = parse_embedding(user.voice_embedding)
        log.info(f"   📦 Enrolled embedding: dim={len(enrolled_embedding)}, first 3={enrolled_embedding[:3]}")

        # ── Layer 1 — Speaker Similarity (Resemblyzer) ──
        log.info("   ──────────────────────────────────────")
        log.info("   🔊 LAYER 1: Speaker Similarity (cosine)")
        layer1 = compare_embeddings(enrolled_embedding, test_embedding)
        log.info(f"      similarity:  {layer1['similarity']:.4f}")
        log.info(f"      threshold:   {layer1['threshold']}")
        log.info(f"      match:       {'YES ✅' if layer1['match'] else 'NO ❌'}")
        log.info(f"      confidence:  {layer1['confidence']:.4f}")

        # Short-circuit: if Layer 1 already failed, skip the Gemini call
        if not layer1["match"]:
            log.info("   ──────────────────────────────────────")
            log.info(f"   🔴 VERDICT: FAILED — speaker mismatch (sim={layer1['similarity']:.4f})")
            log.info("   ⏭️ Skipping Layer 2 (Gemini) — no point if voice doesn't match")
            fail_reasons = [f"Speaker mismatch (similarity: {layer1['similarity']:.2f})"]
            # ── Solana audit trail ──
            sol_tx = log_verification_attempt(
                session_id=session_id,
                external_user_id=session.external_user_id,
                audio_bytes=audio_bytes,
                result="failed",
                similarity=layer1["similarity"],
                reasons=fail_reasons,
            )
            log.info("🔵" + "="*53)
            return SessionVerifyResponse(
                status="failed",
                message="Verification failed — voice did not match enrolled profile.",
                confidence_score=layer1["confidence"],
                similarity=layer1["similarity"],
                reasons=fail_reasons,
                solana_tx=sol_tx,
            )

        # ── Layer 2 — Human Comprehension via Gemini ──
        # Only runs if Layer 1 passed (voice matches enrolled profile)
        # Retrieve the SAME instruction that was shown to the user in session_status
        log.info("   ──────────────────────────────────────")
        log.info("   🧠 LAYER 2: Human Comprehension (Gemini)")
        session_key = store.k_verification_session(session_id)
        instruction = store.r.hget(session_key, 'challenge_instruction') or ''
        expected_behavior = store.r.hget(session_key, 'challenge_expected_behavior') or ''
        log.info(f"      instruction (from session): {instruction}")

        layer2 = comprehension_check(
            audio_data=audio_bytes,
            instruction=instruction,
            expected_behavior=expected_behavior,
            similarity_score=layer1['similarity'],
        )
        log.info(f"      followed_instruction: {layer2.get('followed_instruction', 'N/A')}")
        log.info(f"      confidence:            {layer2.get('confidence', 'N/A')}")
        log.info(f"      recommendation:        {layer2.get('recommendation', 'N/A')}")
        log.info(f"      reasoning:             {layer2.get('reasoning', 'N/A')}")
        if layer2.get('red_flags'):
            log.warning(f"      🚩 red_flags: {layer2['red_flags']}")
        if layer2.get('skipped'):
            log.warning(f"      ⚠️  Comprehension skipped: {layer2.get('reason', 'unknown')}")

        # ── Decision Engine ──
        # (Layer 1 already passed if we got here)
        log.info("   ──────────────────────────────────────")
        log.info("   🧠 DECISION ENGINE")
        log.info(f"      ✅ PASS: speaker match (sim={layer1['similarity']:.4f})")
        reasons: list[str] = []
        failed = False

        # Layer 2 check (skip if Gemini key not configured)
        if not layer2.get('skipped'):
            if layer2.get('recommendation') == 'BLOCK':
                failed = True
                reasons.append(f"Comprehension failed: {layer2.get('reasoning', 'TTS/AI behavior detected')}")
                log.info(f"      ❌ FAIL: comprehension BLOCK — {layer2.get('reasoning', '')}")
            elif layer2.get('recommendation') == 'CHALLENGE_AGAIN':
                failed = True
                reasons.append(f"Unclear response: {layer2.get('reasoning', 'Please try again')}")
                log.info(f"      ⚠️ FAIL: comprehension CHALLENGE_AGAIN — {layer2.get('reasoning', '')}")
            else:
                log.info(f"      ✅ PASS: comprehension ALLOW (confidence={layer2.get('confidence', 0):.2f})")
        else:
            log.info(f"      ⏭️ SKIP: comprehension layer skipped ({layer2.get('reason', '')})")

        overall = layer1["confidence"]
        if not layer2.get('skipped') and layer2.get('confidence') is not None:
            overall = (layer1["confidence"] + float(layer2["confidence"])) / 2.0
        log.info(f"      overall confidence: {overall:.4f}")

        log.info("   ──────────────────────────────────────")
        if failed:
            log.info(f"   🔴 VERDICT: FAILED — {reasons}")
            # ── Solana audit trail ──
            sol_tx = log_verification_attempt(
                session_id=session_id,
                external_user_id=session.external_user_id,
                audio_bytes=audio_bytes,
                result="failed",
                similarity=layer1["similarity"],
                comprehension_recommendation=layer2.get('recommendation'),
                reasons=reasons or ["verification_failed"],
            )
            log.info("🔵" + "="*53)
            return SessionVerifyResponse(
                status="failed",
                message="Verification failed — voice did not pass security checks.",
                confidence_score=overall,
                similarity=layer1["similarity"],
                comprehension=layer2 if not layer2.get('skipped') else None,
                reasons=reasons or ["verification_failed"],
                solana_tx=sol_tx,
            )

        log.info("   ✅ VERDICT: VERIFIED — all security checks passed!")
        log.info(f"      similarity:  {layer1['similarity']:.4f}")
        log.info(f"      confidence:  {overall:.4f}")
        # ── Solana audit trail ──
        sol_tx = log_verification_attempt(
            session_id=session_id,
            external_user_id=session.external_user_id,
            audio_bytes=audio_bytes,
            result="verified",
            similarity=layer1["similarity"],
            comprehension_recommendation=layer2.get('recommendation'),
            reasons=["all_checks_passed"],
        )
        log.info("🔵" + "="*53)
        return SessionVerifyResponse(
            status="verified",
            message="Voice verified successfully!",
            confidence_score=overall,
            similarity=layer1["similarity"],
            comprehension=layer2 if not layer2.get('skipped') else None,
            reasons=["all_checks_passed"],
            solana_tx=sol_tx,
        )

    except Exception as e:
        log.error(f"   💀 VERIFICATION EXCEPTION: {e}")
        log.exception(e)
        return SessionVerifyResponse(
            status="failed",
            message=f"Verification error: {e!s}",
            reasons=[f"error: {e!s}"],
        )


# =====================================================================
# Serve React static files in production
# =====================================================================
DIST_DIR = Path(__file__).parent.parent / "dist"

if DIST_DIR.exists():
    # Serve static assets from the Vite build output
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Catch-all: serve index.html for client-side routing."""
        file_path = DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(DIST_DIR / "index.html"))
