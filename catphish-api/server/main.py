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

from db.valkey_store import ValkeyStore, Tenant
from voice.encoder import create_embedding
from voice.verification import compare_embeddings
from voice.ai_detection import detect_ai
from voice.comprehension import comprehension_check
from voice.audio_utils import base64_to_bytes

load_dotenv()

APP_NAME = "catphish-api"
API_VERSION = "v1"

# ---- config ----
VALKEY_HOST = os.getenv("VALKEY_HOST", "127.0.0.1")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "6379"))
DEFAULT_TTL_SECONDS = int(os.getenv("CHALLENGE_TTL_SECONDS", "120"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))

store = ValkeyStore(host=VALKEY_HOST, port=VALKEY_PORT)

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
    ai_probability: Optional[float] = None


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
    ai_probability: Optional[float] = None
    reasons: Optional[List[str]] = None


# =====================================================================
# Helpers
# =====================================================================
def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def require_tenant(
    x_catphish_key: Optional[str] = Header(default=None, alias="X-Catphish-Key"),
) -> Tenant:
    if not x_catphish_key:
        raise HTTPException(status_code=401, detail="Missing X-Catphish-Key")
    tenant = store.get_tenant_by_api_key(x_catphish_key.strip())
    if not tenant or not tenant.tenant_id:
        raise HTTPException(status_code=401, detail="Invalid tenant API key")
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
    try:
        pong = store.r.ping()
        return HealthResponse(
            ok=bool(pong),
            valkey=f"{VALKEY_HOST}:{VALKEY_PORT}",
            timestamp=int(time.time()),
        )
    except Exception as e:
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
        layer2_result = compare_embeddings(enrolled_embedding, test_embedding)
        layer3_result = detect_ai(audio_bytes)
        layer4_result = None
        if ch.phrase:
            layer4_result = comprehension_check(
                audio_bytes,
                ch.phrase,
                similarity_score=layer2_result["similarity"],
                ai_probability=layer3_result["ai_probability"],
            )

        reasons: list[str] = []
        failed = False

        if not layer2_result["match"]:
            failed = True
            reasons.append(f"speaker_mismatch (similarity: {layer2_result['similarity']:.2f})")
        if layer3_result["is_ai"]:
            failed = True
            reasons.append(f"ai_detected (probability: {layer3_result['ai_probability']:.2f})")
        if layer4_result and not layer4_result.get("skipped"):
            if layer4_result.get("recommendation") == "BLOCK":
                failed = True
                reasons.append(f"comprehension_failed: {layer4_result.get('reasoning', 'Unknown')}")
            elif layer4_result.get("recommendation") == "CHALLENGE_AGAIN":
                failed = True
                reasons.append(f"challenge_again: {layer4_result.get('reasoning', 'Unknown')}")

        confidences = [layer2_result["confidence"]]
        if layer3_result.get("confidence") is not None:
            confidences.append(layer3_result["confidence"])
        if (
            layer4_result
            and not layer4_result.get("skipped")
            and layer4_result.get("match_confidence") is not None
        ):
            confidences.append(layer4_result["match_confidence"])

        import numpy as np

        overall_confidence = float(np.mean(confidences)) if confidences else 0.0

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
        similarity=layer2_result["similarity"],
        ai_probability=layer3_result["ai_probability"],
    )


# =====================================================================
# Routes — Session-Based Frontend API (no X-Catphish-Key needed)
#
# These endpoints are called directly by the React verification frontend.
# Auth is via the session_id itself (which maps to a tenant + user).
# =====================================================================

def _resolve_session(session_id: str):
    """Look up a verification session and its associated tenant/user."""
    session = store.get_verification_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
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
    session = _resolve_session(session_id)
    user = store.get_user(session.tenant_id, session.external_user_id)
    enrolled = bool(user and user.voice_embedding)
    phrase = generate_phrase()
    return SessionStatusResponse(
        session_id=session_id,
        external_user_id=session.external_user_id,
        return_url=session.return_url,
        enrolled=enrolled,
        phrase=phrase,
    )


@app.post(f"/{API_VERSION}/session/{{session_id}}/enroll", response_model=SessionEnrollResponse)
def session_enroll(session_id: str, req: SessionEnrollRequest):
    """
    First-time user: record voice → create embedding → store it.
    Called by the verification frontend when user is NOT yet enrolled.
    """
    session = _resolve_session(session_id)

    try:
        audio_bytes = base64_to_bytes(req.audio_sample)
        embedding = create_embedding(audio_bytes)
        embedding_list = embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Audio processing failed: {e}")

    store.upsert_user_embedding(
        tenant_id=session.tenant_id,
        external_user_id=session.external_user_id,
        voice_embedding=embedding_list,
        created_at_iso=now_iso(),
    )

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
    session = _resolve_session(session_id)
    user = store.get_user(session.tenant_id, session.external_user_id)

    if not user or not user.voice_embedding:
        return SessionVerifyResponse(
            status="failed",
            message="No voice profile found. Please enroll first.",
            reasons=["user_not_enrolled"],
        )

    # Rate limit
    allowed, count, ttl = store.check_rate_limit(
        tenant_id=session.tenant_id,
        external_user_id=session.external_user_id,
        limit=RATE_LIMIT_PER_MINUTE,
        window_seconds=60,
    )
    if not allowed:
        return SessionVerifyResponse(
            status="failed",
            message=f"Too many attempts. Try again in {ttl} seconds.",
            reasons=["rate_limited"],
        )

    try:
        audio_bytes = base64_to_bytes(req.audio_sample)

        # Layer 1 — create embedding from test audio
        test_embedding = create_embedding(audio_bytes)
        enrolled_embedding = parse_embedding(user.voice_embedding)

        # Layer 2 — speaker similarity
        layer2 = compare_embeddings(enrolled_embedding, test_embedding)

        # Layer 3 — AI detection
        layer3 = detect_ai(audio_bytes)

        # Diagnostics
        reasons: list[str] = []
        failed = False

        if not layer2["match"]:
            failed = True
            reasons.append(f"Speaker mismatch (similarity: {layer2['similarity']:.2f})")

        if layer3["is_ai"]:
            failed = True
            reasons.append(f"AI voice detected (probability: {layer3['ai_probability']:.2f})")

        confidences = [layer2["confidence"]]
        if layer3.get("confidence") is not None:
            confidences.append(layer3["confidence"])

        import numpy as np
        overall = float(np.mean(confidences)) if confidences else 0.0

        if failed:
            return SessionVerifyResponse(
                status="failed",
                message="Verification failed — voice did not pass security checks.",
                confidence_score=overall,
                similarity=layer2["similarity"],
                ai_probability=layer3["ai_probability"],
                reasons=reasons or ["verification_failed"],
            )

        return SessionVerifyResponse(
            status="verified",
            message="Voice verified successfully!",
            confidence_score=overall,
            similarity=layer2["similarity"],
            ai_probability=layer3["ai_probability"],
            reasons=["all_checks_passed"],
        )

    except Exception as e:
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
