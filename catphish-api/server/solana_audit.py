"""
Solana Audit Trail — writes immutable verification logs on-chain.

Every Catphish verification attempt (pass or fail) gets a memo
transaction on Solana containing a JSON payload with:
  - timestamp
  - session_id
  - user_id_hash  (SHA-256 of external_user_id — no PII on-chain)
  - audio_hash    (SHA-256 of the raw audio bytes)
  - result        (verified / failed)
  - similarity    (Layer 1 cosine score)
  - comprehension (Layer 2 Gemini recommendation)
  - reasons       (why it passed / failed)

Uses the Solana Memo Program (MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr)
on devnet for near-zero-cost, immutable audit logging.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Optional

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solders.hash import Hash
from solana.rpc.api import Client

log = logging.getLogger("catphish.solana")

# ── Constants ──
MEMO_PROGRAM_ID = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")
DEVNET_URL = "https://api.devnet.solana.com"


def _get_client() -> Client:
    url = os.getenv("SOLANA_RPC_URL", DEVNET_URL)
    return Client(url)


def _get_keypair() -> Optional[Keypair]:
    """
    Load the audit wallet keypair from env.
    SOLANA_PRIVATE_KEY should be a base58-encoded secret key
    or a JSON array of 64 bytes.
    """
    key_str = os.getenv("SOLANA_PRIVATE_KEY", "")
    if not key_str:
        return None

    try:
        # Try JSON array of bytes first (Solana CLI format)
        if key_str.startswith("["):
            key_bytes = bytes(json.loads(key_str))
            return Keypair.from_bytes(key_bytes)
        # Otherwise treat as base58
        return Keypair.from_base58_string(key_str)
    except Exception as e:
        log.error(f"Failed to load Solana keypair: {e}")
        return None


def _hash_data(data: bytes | str) -> str:
    """SHA-256 hash, returned as hex string."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_audit_memo(
    session_id: str,
    external_user_id: str,
    audio_bytes: bytes,
    result: str,
    similarity: Optional[float] = None,
    comprehension_recommendation: Optional[str] = None,
    reasons: Optional[list[str]] = None,
) -> dict:
    """
    Build the JSON memo payload for on-chain logging.
    All PII is hashed — only fingerprints go on-chain.
    """
    memo = {
        "v": 1,                                        # schema version
        "app": "catphish",
        "ts": int(time.time()),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session": session_id,
        "user_hash": _hash_data(external_user_id),    # no PII on-chain
        "audio_hash": _hash_data(audio_bytes),         # fingerprint of recording
        "result": result,                              # "verified" | "failed"
    }
    if similarity is not None:
        memo["similarity"] = round(similarity, 4)
    if comprehension_recommendation:
        memo["comprehension"] = comprehension_recommendation
    if reasons:
        memo["reasons"] = reasons

    return memo


def submit_audit_memo(memo: dict) -> dict:
    """
    Submit a memo transaction to Solana.

    Returns:
        dict with:
            - success: bool
            - signature: str (tx signature) or None
            - explorer_url: str or None
            - error: str or None
            - memo: dict (the payload that was written)
    """
    keypair = _get_keypair()
    if not keypair:
        log.warning("⚠️ SOLANA_PRIVATE_KEY not set — audit trail skipped")
        return {
            "success": False,
            "signature": None,
            "explorer_url": None,
            "error": "SOLANA_PRIVATE_KEY not configured",
            "memo": memo,
        }

    client = _get_client()
    memo_json = json.dumps(memo, separators=(",", ":"))  # compact JSON

    # Memo must be ≤ 566 bytes
    memo_bytes = memo_json.encode("utf-8")
    if len(memo_bytes) > 566:
        # Truncate reasons if too long
        memo["reasons"] = [memo["reasons"][0][:80]] if memo.get("reasons") else []
        memo_json = json.dumps(memo, separators=(",", ":"))
        memo_bytes = memo_json.encode("utf-8")

    try:
        # Build memo instruction
        memo_ix = Instruction(
            program_id=MEMO_PROGRAM_ID,
            accounts=[AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True)],
            data=memo_bytes,
        )

        # Get recent blockhash
        blockhash_resp = client.get_latest_blockhash()
        recent_blockhash = blockhash_resp.value.blockhash

        # Build & sign transaction
        msg = Message.new_with_blockhash(
            [memo_ix],
            keypair.pubkey(),
            recent_blockhash,
        )
        tx = Transaction.new_unsigned(msg)
        tx.sign([keypair], recent_blockhash)

        # Send
        resp = client.send_transaction(tx)
        signature = str(resp.value)

        rpc_url = os.getenv("SOLANA_RPC_URL", DEVNET_URL)
        cluster = "devnet" if "devnet" in rpc_url else "mainnet-beta"
        explorer_url = f"https://explorer.solana.com/tx/{signature}?cluster={cluster}"

        log.info(f"✅ Solana audit trail written: {signature}")
        log.info(f"   🔗 {explorer_url}")

        return {
            "success": True,
            "signature": signature,
            "explorer_url": explorer_url,
            "error": None,
            "memo": memo,
        }

    except Exception as e:
        log.error(f"❌ Solana audit trail failed: {e}")
        return {
            "success": False,
            "signature": None,
            "explorer_url": None,
            "error": str(e),
            "memo": memo,
        }


def log_verification_attempt(
    session_id: str,
    external_user_id: str,
    audio_bytes: bytes,
    result: str,
    similarity: Optional[float] = None,
    comprehension_recommendation: Optional[str] = None,
    reasons: Optional[list[str]] = None,
) -> dict:
    """
    High-level helper: build memo + submit to Solana.
    Called from the verification endpoint after the decision is made.
    """
    memo = build_audit_memo(
        session_id=session_id,
        external_user_id=external_user_id,
        audio_bytes=audio_bytes,
        result=result,
        similarity=similarity,
        comprehension_recommendation=comprehension_recommendation,
        reasons=reasons,
    )
    return submit_audit_memo(memo)
