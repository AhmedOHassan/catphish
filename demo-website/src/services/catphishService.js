/**
 * Catphish Voice Verification API Service
 * 
 * Integrates with the Catphish Voice Verification Frontend
 * 
 * Flow:
 * 1. Demo website creates verification session via API
 * 2. Demo website redirects to catphish-api with session_id only
 * 3. User completes verification on catphish-api
 * 4. Catphish-api redirects back with result
 */

// Catphish API Backend URL (running on port 8000)
const CATPHISH_API_URL = 'http://localhost:8000';
// Catphish API Frontend URL (running on port 3001)
const CATPHISH_FRONTEND_URL = 'http://localhost:3001';
// Demo tenant API key (for development)
const DEMO_API_KEY = 'demo_key_12345';

/**
 * Redirects to Catphish voice verification frontend
 * @param {string} external_user_id - The user's ID from your system
 * @param {string} return_url - URL to return to after verification
 */
export async function redirectToVoiceVerification(external_user_id, return_url = null) {
  const returnTo = return_url || `${window.location.origin}/dashboard`;
  
  console.log("🎤 Creating verification session:", {
    external_user_id,
    return_url: returnTo,
  });
  
  try {
    // Call API to create verification session
    const response = await fetch(`${CATPHISH_API_URL}/v1/verification-sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Catphish-Key': DEMO_API_KEY,
      },
      body: JSON.stringify({
        external_user_id: external_user_id,
        return_url: returnTo,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create verification session: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log("✅ Verification session created:", data.session_id);
    
    // Redirect to verification page with session_id only
    window.location.href = data.verification_url;
  } catch (error) {
    console.error("❌ Error creating verification session:", error);
    // Fallback: redirect with error
    alert("Failed to initiate verification. Please try again.");
    throw error;
  }
}

/**
 * Checks verification result from URL parameters (after redirect back)
 * @returns {object|null} - Verification result or null if no result
 */
export function getVerificationResult() {
  const urlParams = new URLSearchParams(window.location.search);
  const status = urlParams.get('verification_status');
  const sessionId = urlParams.get('session_id');
  
  if (status) {
    return {
      status: status === 'success' ? 200 : 401,
      session_id: sessionId || 'unknown',
      verified: status === 'success'
    };
  }
  
  return null;
}

/**
 * Returns to the original application after verification
 * @param {boolean} success - Whether verification was successful
 * @param {string} session_id - The verification session ID
 */
export function returnFromVerification(success, session_id = null) {
  const returnUrl = localStorage.getItem('catphish_return_url') || '/dashboard';
  
  // Clean up
  localStorage.removeItem('catphish_return_url');
  
  // Redirect back with status
  const url = new URL(returnUrl, window.location.origin);
  url.searchParams.set('verification_status', success ? 'success' : 'failure');
  if (session_id) {
    url.searchParams.set('session_id', session_id);
  }
  
  window.location.href = url.toString();
}

/**
 * Legacy function for backward compatibility
 * Now creates a verification session and redirects to the frontend
 */
export async function createVerificationSession(external_user_id) {
  console.log("🎤 Using Catphish Voice Verification Frontend");
  
  // Create session and redirect to catphish-api
  await redirectToVoiceVerification(external_user_id);
  
  // Return a pending promise that never resolves since we're redirecting
  return new Promise(() => {});
}
