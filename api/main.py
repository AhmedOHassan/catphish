from __future__ import annotations

import json
import os
import secrets
import time
from typing import Optional, Literal, List, Any

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from db.valkey_store import ValkeyStore, Tenant
from voice.encoder import create_embedding
from voice.verification import compare_embeddings
from voice.ai_detection import detect_ai
from voice.comprehension import comprehension_check
from voice.audio_utils import base64_to_bytes

load_dotenv()  # loads .env from repo root when running from repo root

APP_NAME = "catphish-api"
API_VERSION = "v1"

# ---- config (safe defaults for hackathon) ----
VALKEY_HOST = os.getenv("VALKEY_HOST", "127.0.0.1")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "6379"))

DEFAULT_TTL_SECONDS = int(os.getenv("CHALLENGE_TTL_SECONDS", "120"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))

# Global store (simple MVP)
store = ValkeyStore(host=VALKEY_HOST, port=VALKEY_PORT)

app = FastAPI(title=APP_NAME, version="0.1.0")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Models
# -------------------------
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


# -------------------------
# Helpers
# -------------------------
def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def require_tenant(x_catphish_key: Optional[str] = Header(default=None, alias="X-Catphish-Key")) -> Tenant:
    if not x_catphish_key:
        raise HTTPException(status_code=401, detail="Missing X-Catphish-Key")

    tenant = store.get_tenant_by_api_key(x_catphish_key.strip())
    if not tenant or not tenant.tenant_id:
        raise HTTPException(status_code=401, detail="Invalid tenant API key")

    return tenant


def generate_phrase() -> str:
    # MVP: fixed pool of tongue-twister-ish phrases (fast + deterministic)
    phrases = [
        "Unique New York, blue alpaca seven",
        "Red leather, yellow leather, nine times fast",
        "Toy boat, toy boat, toy boat, sixteen",
        "She sells seashells by the seashore, twice",
        "Six slick slimy snails, under thirteen bridges",
    ]
    return secrets.choice(phrases)


def parse_embedding(voice_embedding: Any) -> list:
    """
    Parse voice embedding from storage format to list.
    Handles both string (JSON) and list formats.
    
    Args:
        voice_embedding: Embedding in string or list format
        
    Returns:
        list: Parsed embedding as list of floats
    """
    if isinstance(voice_embedding, str):
        return json.loads(voice_embedding)
    return voice_embedding


# -------------------------
# Routes
# -------------------------
@app.get("/health", response_model=HealthResponse)
def health():
    try:
        pong = store.r.ping()
        return HealthResponse(ok=bool(pong), valkey=f"{VALKEY_HOST}:{VALKEY_PORT}", timestamp=int(time.time()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Valkey health check failed: {e}")


@app.post(f"/{API_VERSION}/verification-sessions", response_model=CreateVerificationSessionResponse, status_code=201)
def create_verification_session(req: CreateVerificationSessionRequest, tenant: Tenant = Depends(require_tenant)):
    """
    Create a verification session that returns a session_id.
    The session stores user_id and return_url server-side.
    """
    # Generate session ID
    session_id = "vs_" + secrets.token_hex(16)
    
    # Store session in Valkey with TTL (10 minutes)
    store.create_verification_session(
        session_id=session_id,
        tenant_id=tenant.tenant_id,
        external_user_id=req.external_user_id,
        return_url=req.return_url,
        ttl_seconds=600,
    )
    
    # Build verification URL with only session_id
    frontend_url = os.getenv("CATPHISH_FRONTEND_URL", "http://localhost:3001")
    verification_url = f"{frontend_url}/verify?session_id={session_id}"
    
    return CreateVerificationSessionResponse(
        session_id=session_id,
        verification_url=verification_url,
    )


@app.get(f"/{API_VERSION}/verification-sessions/{{session_id}}", response_model=GetVerificationSessionResponse)
def get_verification_session(session_id: str, tenant: Tenant = Depends(require_tenant)):
    """
    Get verification session information by session_id.
    Used by the frontend to retrieve user_id and return_url.
    """
    session = store.get_verification_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Verification session not found or expired")
    
    # Verify tenant matches
    if session.tenant_id != tenant.tenant_id:
        raise HTTPException(status_code=403, detail="Session belongs to different tenant")
    
    return GetVerificationSessionResponse(
        session_id=session.session_id,
        external_user_id=session.external_user_id,
        return_url=session.return_url,
    )


@app.post(f"/{API_VERSION}/enroll", response_model=EnrollmentResponse)
def enroll(req: EnrollmentRequest, tenant: Tenant = Depends(require_tenant)):
    # Compute real voice embedding
    try:
        audio_bytes = base64_to_bytes(req.audio_sample)
        embedding = create_embedding(audio_bytes)
        # Convert numpy array to list for JSON serialization
        embedding_list = embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process audio: {str(e)}")

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


@app.post(f"/{API_VERSION}/challenges", response_model=CreateChallengeResponse, status_code=201)
def create_challenge(req: CreateChallengeRequest, tenant: Tenant = Depends(require_tenant)):
    # Require user to be enrolled
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

    # In demo, this is your hosted challenge UI route (frontend will implement)
    base_url = os.getenv("PUBLIC_BASE_URL", "https://catphish.tech")
    challenge_url = f"{base_url}/challenge/{challenge_id}"

    return CreateChallengeResponse(
        challenge_id=challenge_id,
        external_user_id=req.external_user_id,
        phrase=phrase,
        expires_in_seconds=ttl,
        challenge_url=challenge_url,
    )


@app.post(f"/{API_VERSION}/challenges" + "/{challenge_id}/verify", response_model=VerifyChallengeResponse)
def verify_challenge(challenge_id: str, req: VerifyChallengeRequest, tenant: Tenant = Depends(require_tenant)):
    # Rate limit first (cheap)
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

    # Anti-replay lock
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

    # Ensure caller is verifying for the same user
    if ch.external_user_id != req.external_user_id:
        # treat as failed (could also be 400)
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="failed",
            confidence_score=0.0,
            risk_level="high",
            reasons=["external_user_id_mismatch"],
        )

    # Get enrolled user embedding
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

    # Run real verification pipeline
    try:
        # Decode audio
        audio_bytes = base64_to_bytes(req.audio_sample)
        
        # Layer 1: Create test embedding
        test_embedding = create_embedding(audio_bytes)
        
        # Layer 2: Speaker verification
        enrolled_embedding = parse_embedding(user.voice_embedding)
        layer2_result = compare_embeddings(enrolled_embedding, test_embedding)
        
        # Layer 3: AI detection
        layer3_result = detect_ai(audio_bytes)
        
        # Layer 4: Comprehension check (if phrase exists)
        layer4_result = None
        if ch.phrase:
            layer4_result = comprehension_check(
                audio_bytes,
                ch.phrase,
                similarity_score=layer2_result['similarity'],
                ai_probability=layer3_result['ai_probability']
            )
        
        # Make final decision
        reasons = []
        failed = False
        
        # Check Layer 2
        if not layer2_result['match']:
            failed = True
            reasons.append(f"speaker_mismatch (similarity: {layer2_result['similarity']:.2f})")
        
        # Check Layer 3
        if layer3_result['is_ai']:
            failed = True
            reasons.append(f"ai_detected (probability: {layer3_result['ai_probability']:.2f})")
        
        # Check Layer 4
        if layer4_result and not layer4_result.get('skipped'):
            if layer4_result.get('recommendation') == 'BLOCK':
                failed = True
                reasons.append(f"comprehension_failed: {layer4_result.get('reasoning', 'Unknown')}")
            elif layer4_result.get('recommendation') == 'CHALLENGE_AGAIN':
                failed = True
                reasons.append(f"challenge_again: {layer4_result.get('reasoning', 'Unknown')}")
        
        # Calculate overall confidence
        confidences = [layer2_result['confidence']]
        if layer3_result.get('confidence') is not None:
            confidences.append(layer3_result['confidence'])
        if layer4_result and not layer4_result.get('skipped') and layer4_result.get('match_confidence') is not None:
            confidences.append(layer4_result['match_confidence'])
        
        import numpy as np
        overall_confidence = float(np.mean(confidences)) if confidences else 0.0
        
        # Determine status and risk
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
        # Handle verification errors
        return VerifyChallengeResponse(
            challenge_id=challenge_id,
            external_user_id=req.external_user_id,
            status="failed",
            confidence_score=0.0,
            risk_level="high",
            reasons=[f"verification_error: {str(e)}"],
        )

    # Optional: store status while TTL remains
    store.set_challenge_status(tenant.tenant_id, challenge_id, status)

    return VerifyChallengeResponse(
        challenge_id=challenge_id,
        external_user_id=req.external_user_id,
        status=status,
        confidence_score=overall_confidence,
        risk_level=risk,
        reasons=reasons,
        similarity=layer2_result['similarity'],
        ai_probability=layer3_result['ai_probability'],
    )

