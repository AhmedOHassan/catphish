/**
 * Catphish API Client for direct backend integration
 * 
 * This client directly calls the Catphish backend API endpoints:
 * - POST /v1/enroll
 * - POST /v1/challenges
 * - POST /v1/challenges/{id}/verify
 */

/**
 * Enroll a user with their voice sample
 * @param {Object} params - Enrollment parameters
 * @param {string} params.external_user_id - User ID from your system
 * @param {string} params.audio_sample_base64 - Base64 encoded audio (WAV format)
 * @param {Object} params.metadata - Optional metadata
 * @param {string} params.apiBaseUrl - API base URL (e.g., http://127.0.0.1:8000)
 * @param {string} params.apiKey - X-Catphish-Key header value
 * @returns {Promise<Object>} Enrollment response
 */
export async function enroll({ external_user_id, audio_sample_base64, metadata = null, apiBaseUrl, apiKey }) {
  console.log('📤 Enrolling user:', external_user_id);
  
  const response = await fetch(`${apiBaseUrl}/v1/enroll`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Catphish-Key': apiKey,
    },
    body: JSON.stringify({
      external_user_id,
      audio_sample: audio_sample_base64,
      metadata,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(`Enrollment failed: ${error.detail || response.statusText}`);
  }

  const data = await response.json();
  console.log('✅ Enrollment successful:', data);
  return data;
}

/**
 * Create a challenge for verification
 * @param {Object} params - Challenge parameters
 * @param {string} params.external_user_id - User ID from your system
 * @param {string} params.purpose - Purpose of challenge (default: "login")
 * @param {number} params.ttl_seconds - Challenge TTL (default: 120)
 * @param {string} params.apiBaseUrl - API base URL
 * @param {string} params.apiKey - X-Catphish-Key header value
 * @returns {Promise<Object>} Challenge response with challenge_id and phrase
 */
export async function createChallenge({ external_user_id, purpose = 'login', ttl_seconds = 120, apiBaseUrl, apiKey }) {
  console.log('📤 Creating challenge for user:', external_user_id);
  
  const response = await fetch(`${apiBaseUrl}/v1/challenges`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Catphish-Key': apiKey,
    },
    body: JSON.stringify({
      external_user_id,
      purpose,
      ttl_seconds,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(`Challenge creation failed: ${error.detail || response.statusText}`);
  }

  const data = await response.json();
  console.log('✅ Challenge created:', data);
  return data;
}

/**
 * Verify a challenge with voice sample
 * @param {Object} params - Verification parameters
 * @param {string} params.challenge_id - Challenge ID to verify
 * @param {string} params.external_user_id - User ID from your system
 * @param {string} params.audio_sample_base64 - Base64 encoded audio (WAV format)
 * @param {string} params.apiBaseUrl - API base URL
 * @param {string} params.apiKey - X-Catphish-Key header value
 * @returns {Promise<Object>} Verification response with status and metrics
 */
export async function verify({ challenge_id, external_user_id, audio_sample_base64, apiBaseUrl, apiKey }) {
  console.log('📤 Verifying challenge:', challenge_id);
  
  const response = await fetch(`${apiBaseUrl}/v1/challenges/${challenge_id}/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Catphish-Key': apiKey,
    },
    body: JSON.stringify({
      external_user_id,
      audio_sample: audio_sample_base64,
      client_timestamp: new Date().toISOString(),
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(`Verification failed: ${error.detail || response.statusText}`);
  }

  const data = await response.json();
  console.log('✅ Verification complete:', data);
  return data;
}
