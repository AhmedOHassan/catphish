# Catphish API (MVP) — `api.md`

Catphish is a voice-based step-up verification service designed to be dropped into an existing authentication flow (e.g., banking login, high-risk transfer, account recovery).  
For the MVP, Catphish stores only **tenants** and **users** (voice embeddings) and manages **challenges** ephemerally (TTL) in Valkey.

---

## Current Data Model (MVP)

> **Source of truth for MVP**: Valkey-only storage, modeled as two conceptual tables.

### 🟢 1) `tenants`
Stores companies using Catphish.

- `id` (uuid, primary key)
- `name` (text)
- `api_key` (text)
- `created_at` (timestamp)

### 🟢 2) `users`
Stores enrolled voice embeddings per tenant.

- `id` (uuid, primary key)
- `tenant_id` (uuid, foreign key → tenants.id)
- `external_user_id` (text)
- `voice_embedding` (jsonb or vector)
- `created_at` (timestamp)

**Constraint:** `UNIQUE (tenant_id, external_user_id)`

---

## Authentication

### Tenant API Key
All requests must include an API key identifying the tenant.

**Header**
- `X-Catphish-Key: <api_key>`

**Behavior**
- If the key is missing/invalid → `401 Unauthorized`
- If valid → request is scoped to that tenant

> **MVP note:** API keys are stored and compared directly (no hashing). Production should store a hash and support rotation.

---

## Status Codes (MVP)

- `200 OK` — request succeeded
- `201 Created` — resource created (enrollment/challenge)
- `400 Bad Request` — missing/invalid fields
- `401 Unauthorized` — invalid tenant API key
- `404 Not Found` — user/challenge not found (or expired)
- `409 Conflict` — challenge already used / replay attempt
- `429 Too Many Requests` — rate-limited
- `500 Internal Server Error` — unexpected failure

---

## Core Concepts

### Enrollment
A tenant enrolls a user by providing an audio sample. Catphish stores a computed `voice_embedding` for future comparisons.

### Challenge (Ephemeral)
A challenge is a time-limited phrase the user must read aloud.  
Challenges are stored ephemerally (TTL) and are **single-use** (anti-replay lock).

---

## Endpoints (MVP)

### 1) Enroll / Update User Voice
Creates or updates a user's stored voice embedding for the current tenant.

**`POST /v1/enroll`**

#### Request JSON
```json
{
  "external_user_id": "user_123",
  "audio_sample": "base64_encoded_audio",
  "metadata": {
    "enrollment_reason": "initial",
    "device": "web"
  }
}
```

#### Response JSON (201 or 200)
```json
{
  "tenant_id": "t_demo",
  "external_user_id": "user_123",
  "enrolled": true,
  "embedding_version": "v1",
  "created_at": "2026-02-14T00:00:00Z"
}
```

#### Notes
- If the user does not exist → create
- If the user exists → overwrite/update `voice_embedding`
- `audio_sample` is processed to compute `voice_embedding`; raw audio should not be stored long-term in MVP unless required for debugging.

---

### 2) Create Challenge
Generates a short, dynamic phrase and creates a time-limited challenge for a specific user.

**`POST /v1/challenges`**

#### Request JSON
```json
{
  "external_user_id": "user_123",
  "purpose": "login",
  "ttl_seconds": 120
}
```

#### Response JSON (201)
```json
{
  "challenge_id": "ch_6c5b0f",
  "external_user_id": "user_123",
  "phrase": "Unique New York, blue alpaca seven",
  "expires_in_seconds": 120,
  "challenge_url": "https://catphish.tech/challenge/ch_6c5b0f"
}
```

#### Server rules
- If user not enrolled → `404 Not Found` (or `409` depending on product choice; MVP uses `404`)
- `ttl_seconds` may be clamped (e.g., min 30, max 180)

---

### 3) Verify Challenge Attempt
Submits audio for a challenge, verifies the phrase was spoken, and returns a decision.

**`POST /v1/challenges/{challenge_id}/verify`**

#### Request JSON
```json
{
  "external_user_id": "user_123",
  "audio_sample": "base64_encoded_audio",
  "client_timestamp": "2026-02-14T00:00:05Z"
}
```

#### Response JSON (200)
```json
{
  "challenge_id": "ch_6c5b0f",
  "external_user_id": "user_123",
  "status": "verified",
  "confidence_score": 0.94,
  "risk_level": "low",
  "reasons": [
    "phrase_match_ok",
    "timing_ok"
  ]
}
```

#### Possible `status` values
- `verified` — accepted
- `failed` — rejected
- `expired` — challenge key missing/TTL elapsed
- `replay_blocked` — challenge already used (lock exists)
- `rate_limited` — too many attempts in window

#### Server rules (MVP)
- **Single-use:** if `challenge_id` has already been verified once, return `409 Conflict` with `status=replay_blocked`
- **Expiry:** if the challenge key is missing, return `404 Not Found` with `status=expired`
- **Tenant isolation:** `challenge_id` must belong to the current tenant (enforced by challenge storage namespace)

---

### 4) Get Challenge Status (Optional)
Allows polling (useful for “bank page” waiting on verification).

**`GET /v1/challenges/{challenge_id}`**

#### Response JSON (200)
```json
{
  "challenge_id": "ch_6c5b0f",
  "external_user_id": "user_123",
  "status": "pending",
  "expires_in_seconds": 71
}
```

#### Notes
- For MVP, status may remain `pending` unless you explicitly store status updates in Valkey.
- If you do not implement this endpoint, the client can rely on the immediate `/verify` response.

---

## Example Developer Flow (Bank Integration)

```js
// Bank-side pseudo-code (after password auth success)
const challenge = await fetch("/v1/challenges", {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-Catphish-Key": CATPHISH_KEY },
  body: JSON.stringify({ external_user_id: userId, purpose: "login", ttl_seconds: 120 })
}).then(r => r.json());

// Redirect user to Catphish challenge UI
window.location.href = challenge.challenge_url;
```

---

## MVP Storage Strategy (Valkey)

This API spec assumes:
- **Tenants** and **Users** persist in Valkey (as structured keys/hashes)
- **Challenges** persist ephemerally in Valkey with TTL
- No `verification_events` table in MVP (audit trail deferred)

> When you add Solana + auditing later, introduce `verification_events` as durable storage and optionally return `solana_tx` and `attestation_hash` from `/verify`.

---

## Non-Goals for MVP
- Full voice biometric accuracy guarantees
- Robust anti-spoof model
- On-chain event storage
- Long-term raw audio retention
- Multi-region resilience

---

## Glossary
- **Tenant**: A company integrating Catphish.
- **External User ID**: The tenant’s user identifier.
- **Voice Embedding**: Numerical representation of a voice used for matching.
- **Challenge**: A dynamic phrase that must be spoken within a short time window.

