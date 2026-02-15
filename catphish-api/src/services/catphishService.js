/**
 * Catphish Voice Verification API Service
 *
 * Talks to the FastAPI backend at /v1/session/* endpoints.
 * In dev mode Vite proxies /v1 → http://localhost:8000.
 */

const API_BASE = import.meta.env.VITE_CATPHISH_API_URL || '';
// If API_BASE is empty, requests go to same origin (works with vite proxy)

/**
 * Fetch session status — tells us if the user is enrolled, gives a phrase, etc.
 */
export async function getSessionStatus(sessionId) {
  const res = await fetch(`${API_BASE}/v1/session/${sessionId}/status`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Session status failed: ${res.status}`);
  }
  return res.json();
  // → { session_id, external_user_id, return_url, enrolled, phrase }
}

/**
 * Enroll voice (first-time user).
 * @param {string} sessionId
 * @param {string} audioBase64 - base64-encoded WAV
 */
export async function enrollVoice(sessionId, audioBase64) {
  const res = await fetch(`${API_BASE}/v1/session/${sessionId}/enroll`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ audio_sample: audioBase64 }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Enrollment failed: ${res.status}`);
  }
  return res.json();
  // → { success, message, enrolled }
}

/**
 * Verify voice (returning user).
 * @param {string} sessionId
 * @param {string} audioBase64 - base64-encoded WAV
 */
export async function verifyVoice(sessionId, audioBase64) {
  const res = await fetch(`${API_BASE}/v1/session/${sessionId}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ audio_sample: audioBase64 }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Verification failed: ${res.status}`);
  }
  return res.json();
  // → { status, message, confidence_score, similarity, ai_probability, reasons }
}

/**
 * Legacy: getSessionInfo for backward compat.
 */
export async function getSessionInfo(sessionId) {
  const data = await getSessionStatus(sessionId);
  return {
    external_user_id: data.external_user_id,
    return_url: data.return_url,
  };
}
