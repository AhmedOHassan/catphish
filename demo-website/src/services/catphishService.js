/**
 * Catphish Voice Verification API Service
 * 
 * Integrates with the Catphish Voice Verification Frontend
 * 
 * Flow:
 * 1. Demo website redirects to catphish-api for voice verification
 * 2. User completes verification on catphish-api
 * 3. Catphish-api redirects back with result
 */

// Catphish API Frontend URL (running on port 3001)
const CATPHISH_FRONTEND_URL = 'http://localhost:3001';

/**
 * Redirects to Catphish voice verification frontend
 * @param {string} external_user_id - The user's ID from your system
 * @param {string} return_url - URL to return to after verification
 */
export function redirectToVoiceVerification(external_user_id, return_url = null) {
  // Store user ID for verification process
  localStorage.setItem('external_user_id', external_user_id);
  
  // Store return URL if not provided, use current origin + /dashboard
  const returnTo = return_url || `${window.location.origin}/dashboard`;
  localStorage.setItem('catphish_return_url', returnTo);
  
  console.log("🎤 Redirecting to Catphish Voice Verification:", {
    external_user_id,
    return_url: returnTo,
    stored_in_localStorage: localStorage.getItem('external_user_id')
  });
  
  // Redirect to catphish-api verification page WITH user ID in URL
  // This solves the cross-origin localStorage issue (localhost:3000 vs localhost:3001)
  window.location.href = `${CATPHISH_FRONTEND_URL}/verify?user_id=${encodeURIComponent(external_user_id)}&return_url=${encodeURIComponent(returnTo)}`;
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
 * Now redirects to the voice verification frontend
 */
export async function createVerificationSession(external_user_id) {
  console.log("🎤 Using Catphish Voice Verification Frontend");
  
  // Redirect to catphish-api instead of making API call
  redirectToVoiceVerification(external_user_id);
  
  // Return a pending promise that never resolves since we're redirecting
  return new Promise(() => {});
}
