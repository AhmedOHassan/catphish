# db/valkey_store.py
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Optional, Dict, Tuple

import redis


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    name: str
    created_at: str


@dataclass(frozen=True)
class UserRecord:
    tenant_id: str
    external_user_id: str
    voice_embedding: Optional[str]  # JSON string for MVP
    created_at: Optional[str]


@dataclass(frozen=True)
class Challenge:
    tenant_id: str
    challenge_id: str
    external_user_id: str
    phrase: str
    expires_at: int
    status: str  # "pending" | "verified" | "failed" (optional)


@dataclass(frozen=True)
class VerificationSession:
    session_id: str
    tenant_id: str
    external_user_id: str
    return_url: Optional[str]
    created_at: int


class ValkeyStore:
    """
    Valkey-only DB layer for Catphish MVP.
    Handles tenants, users, challenges (TTL), replay locks, and rate limiting.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 6379, db: int = 0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    # -------------------------
    # Key helpers
    # -------------------------
    @staticmethod
    def k_tenant_by_api_key(api_key: str) -> str:
        return f"tenant:by_api_key:{api_key}"

    @staticmethod
    def k_user(tenant_id: str, external_user_id: str) -> str:
        return f"user:{tenant_id}:{external_user_id}"

    @staticmethod
    def k_tenant_users(tenant_id: str) -> str:
        return f"tenant_users:{tenant_id}"

    @staticmethod
    def k_challenge(tenant_id: str, challenge_id: str) -> str:
        return f"challenge:{tenant_id}:{challenge_id}"

    @staticmethod
    def k_challenge_lock(tenant_id: str, challenge_id: str) -> str:
        return f"challenge_lock:{tenant_id}:{challenge_id}"

    @staticmethod
    def k_rate_limit(tenant_id: str, external_user_id: str) -> str:
        return f"rl:{tenant_id}:{external_user_id}"

    @staticmethod
    def k_verification_session(session_id: str) -> str:
        return f"verification_session:{session_id}"

    # -------------------------
    # Tenant ops
    # -------------------------
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Tenant]:
        data = self.r.hgetall(self.k_tenant_by_api_key(api_key))
        if not data:
            return None
        return Tenant(
            tenant_id=data.get("tenant_id", ""),
            name=data.get("name", ""),
            created_at=data.get("created_at", ""),
        )

    # -------------------------
    # User ops
    # -------------------------
    def get_user(self, tenant_id: str, external_user_id: str) -> Optional[UserRecord]:
        data = self.r.hgetall(self.k_user(tenant_id, external_user_id))
        if not data:
            return None
        return UserRecord(
            tenant_id=tenant_id,
            external_user_id=external_user_id,
            voice_embedding=data.get("voice_embedding"),
            created_at=data.get("created_at"),
        )

    def upsert_user_embedding(
        self,
        tenant_id: str,
        external_user_id: str,
        voice_embedding: Any,  # list/vec/dict/str
        created_at_iso: Optional[str] = None,
    ) -> UserRecord:
        """
        Stores embedding as JSON string for MVP.
        Adds user to tenant_users set.
        """
        if created_at_iso is None:
            created_at_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        emb_str = voice_embedding if isinstance(voice_embedding, str) else json.dumps(voice_embedding)

        key = self.k_user(tenant_id, external_user_id)
        # HSET returns count of new fields; we don't rely on it.
        self.r.hset(key, mapping={"voice_embedding": emb_str, "created_at": created_at_iso})
        self.r.sadd(self.k_tenant_users(tenant_id), external_user_id)

        return UserRecord(
            tenant_id=tenant_id,
            external_user_id=external_user_id,
            voice_embedding=emb_str,
            created_at=created_at_iso,
        )

    # -------------------------
    # Challenge ops (ephemeral)
    # -------------------------
    def create_challenge(
        self,
        tenant_id: str,
        challenge_id: str,
        external_user_id: str,
        phrase: str,
        ttl_seconds: int = 120,
    ) -> Challenge:
        """
        Creates a challenge hash + sets TTL. Expires automatically.
        """
        ttl_seconds = max(30, min(int(ttl_seconds), 180))
        now = int(time.time())
        expires_at = now + ttl_seconds

        key = self.k_challenge(tenant_id, challenge_id)
        self.r.hset(
            key,
            mapping={
                "external_user_id": external_user_id,
                "phrase": phrase,
                "expires_at": str(expires_at),
                "status": "pending",
            },
        )
        self.r.expire(key, ttl_seconds)

        return Challenge(
            tenant_id=tenant_id,
            challenge_id=challenge_id,
            external_user_id=external_user_id,
            phrase=phrase,
            expires_at=expires_at,
            status="pending",
        )

    def get_challenge(self, tenant_id: str, challenge_id: str) -> Optional[Challenge]:
        key = self.k_challenge(tenant_id, challenge_id)
        data = self.r.hgetall(key)
        if not data:
            return None

        expires_at = int(data.get("expires_at", "0") or "0")
        return Challenge(
            tenant_id=tenant_id,
            challenge_id=challenge_id,
            external_user_id=data.get("external_user_id", ""),
            phrase=data.get("phrase", ""),
            expires_at=expires_at,
            status=data.get("status", "pending"),
        )

    def get_challenge_ttl(self, tenant_id: str, challenge_id: str) -> int:
        """
        Returns TTL seconds remaining, or -2 if missing, -1 if exists with no TTL.
        """
        return int(self.r.ttl(self.k_challenge(tenant_id, challenge_id)))

    def claim_challenge_lock(self, tenant_id: str, challenge_id: str, lock_ttl_seconds: int = 300) -> bool:
        """
        Anti-replay: returns True if lock acquired, False if already used.
        """
        lock_key = self.k_challenge_lock(tenant_id, challenge_id)
        # SET key value NX EX seconds
        resp = self.r.set(lock_key, "1", nx=True, ex=int(lock_ttl_seconds))
        return resp is True

    def set_challenge_status(self, tenant_id: str, challenge_id: str, status: str) -> bool:
        """
        Optional for MVP. Will no-op if challenge expired.
        """
        key = self.k_challenge(tenant_id, challenge_id)
        if not self.r.exists(key):
            return False
        self.r.hset(key, "status", status)
        return True

    # -------------------------
    # Rate limiting
    # -------------------------
    def check_rate_limit(
        self,
        tenant_id: str,
        external_user_id: str,
        limit: int = 5,
        window_seconds: int = 60,
    ) -> Tuple[bool, int, int]:
        """
        Returns: (allowed, current_count, ttl_remaining)
        """
        key = self.k_rate_limit(tenant_id, external_user_id)

        pipe = self.r.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        count, ttl = pipe.execute()

        # if first hit, set expiry
        if ttl == -1:
            self.r.expire(key, int(window_seconds))
            ttl = window_seconds

        allowed = int(count) <= int(limit)
        return allowed, int(count), int(ttl)

    # -------------------------
    # Verification session ops
    # -------------------------
    def create_verification_session(
        self,
        session_id: str,
        tenant_id: str,
        external_user_id: str,
        return_url: Optional[str] = None,
        ttl_seconds: int = 600,
    ) -> VerificationSession:
        """
        Creates a verification session that stores user_id and return_url.
        The session_id is passed in the URL instead of user_id.
        """
        now = int(time.time())
        
        key = self.k_verification_session(session_id)
        self.r.hset(
            key,
            mapping={
                "tenant_id": tenant_id,
                "external_user_id": external_user_id,
                "return_url": return_url or "",
                "created_at": str(now),
            },
        )
        self.r.expire(key, ttl_seconds)
        
        return VerificationSession(
            session_id=session_id,
            tenant_id=tenant_id,
            external_user_id=external_user_id,
            return_url=return_url,
            created_at=now,
        )
    
    def get_verification_session(self, session_id: str) -> Optional[VerificationSession]:
        """
        Retrieves a verification session by session_id.
        """
        key = self.k_verification_session(session_id)
        data = self.r.hgetall(key)
        if not data:
            return None
        
        return VerificationSession(
            session_id=session_id,
            tenant_id=data.get("tenant_id", ""),
            external_user_id=data.get("external_user_id", ""),
            return_url=data.get("return_url") or None,
            created_at=int(data.get("created_at", "0")),
        )

