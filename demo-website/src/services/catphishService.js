/**
 * Catphish Voice Verification API Service
 * 
 * ⚠️ THIS IS A PLACEHOLDER IMPLEMENTATION
 * 
 * Replace this with actual Catphish API integration when ready.
 */

/**
 * Creates a verification session with Catphish API
 * @param {string} external_user_id - The user's ID from your system
 * @returns {Promise<{status: number, session_id: string}>}
 */
export async function createVerificationSession(external_user_id) {
  // TODO: Replace with real Catphish API call later

  console.log("🎤 Sending to Catphish API:", {
    external_user_id: external_user_id
  });

  // Simulate API call delay
  return new Promise((resolve) => {
    setTimeout(() => {
      // Mock successful response
      // Change status to simulate failure (e.g., 401, 500)
      resolve({
        status: 200,
        session_id: "demo_session_123"
      });
    }, 1000);
  });
}

/**
 * When implementing the real API, you'll do something like:
 * 
 * export async function createVerificationSession(external_user_id) {
 *   const response = await fetch('YOUR_CATPHISH_API_URL/verify', {
 *     method: 'POST',
 *     headers: {
 *       'Content-Type': 'application/json',
 *       'Authorization': 'Bearer YOUR_API_KEY'
 *     },
 *     body: JSON.stringify({ external_user_id })
 *   });
 *   
 *   const data = await response.json();
 *   return {
 *     status: response.status,
 *     session_id: data.session_id
 *   };
 * }
 */
