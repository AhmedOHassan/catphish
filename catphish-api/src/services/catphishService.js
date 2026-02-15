/**
 * Catphish Voice Verification API Service
 * 
 * ⚠️ THIS IS A PLACEHOLDER IMPLEMENTATION
 * 
 * Replace this with actual Catphish API integration when ready.
 */

// Load environment variables
const API_URL = import.meta.env.VITE_CATPHISH_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_CATPHISH_API_KEY || 'demo_key_12345';

/**
 * Get session information by session_id
 * @param {string} session_id - The session ID from the URL
 * @returns {Promise<{external_user_id: string, return_url: string}>}
 */
export async function getSessionInfo(session_id) {
  console.log("🔍 Fetching session info for:", session_id);
  
  try {
    const response = await fetch(`${API_URL}/v1/verification-sessions/${session_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Catphish-Key': API_KEY,
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch session: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log("✅ Session info retrieved:", data);
    
    return {
      external_user_id: data.external_user_id,
      return_url: data.return_url,
    };
  } catch (error) {
    console.error("❌ Error fetching session info:", error);
    throw error;
  }
}

/**
 * Generate a random verification phrase
 * @returns {string} - Random phrase for voice verification
 */
export function generateVerificationPhrase() {
  const colors = ['Silver', 'Purple', 'Golden', 'Crimson', 'Azure', 'Emerald'];
  const animals = ['tiger', 'rocket', 'dragon', 'phoenix', 'falcon', 'leopard'];
  const numbers = Math.floor(Math.random() * 99) + 1;
  const verbs = ['jumps', 'dances', 'moves', 'flies', 'runs', 'spins'];
  const adverbs = ['quickly', 'loudly', 'smoothly', 'swiftly', 'gracefully', 'boldly'];

  const color = colors[Math.floor(Math.random() * colors.length)];
  const animal = animals[Math.floor(Math.random() * animals.length)];
  const verb = verbs[Math.floor(Math.random() * verbs.length)];
  const adverb = adverbs[Math.floor(Math.random() * adverbs.length)];

  return `${color} ${animal} ${numbers} ${verb} ${adverb}`;
}

/**
 * Check if user is enrolled (has stored voice)
 * @param {string} external_user_id - The user's ID from your system
 * @returns {Promise<{enrolled: boolean, phrase?: string}>}
 */
export async function checkUserEnrollment(external_user_id) {
  // TODO: Replace with real Catphish API call to check enrollment status
  
  console.log("🔍 Checking enrollment for:", external_user_id);
  
  // Simulate API call delay
  return new Promise((resolve) => {
    setTimeout(() => {
      // Mock response - check localStorage to simulate enrolled users
      const enrolledUsers = JSON.parse(localStorage.getItem('enrolled_users') || '[]');
      const isEnrolled = enrolledUsers.includes(external_user_id);
      
      resolve({
        enrolled: isEnrolled,
        phrase: isEnrolled ? generateVerificationPhrase() : "Silver tiger 42 jumps quickly"
      });
    }, 500);
  });
}

/**
 * Creates a verification session with Catphish API
 * @param {string} external_user_id - The user's ID from your system
 * @param {boolean} isEnrollment - Whether this is an enrollment or verification
 * @returns {Promise<{status: number, session_id?: string, message?: string}>}
 */
export async function createVerificationSession(external_user_id, isEnrollment = false) {
  // TODO: Replace with real Catphish API call when backend is ready
  
  console.log("🎤 Sending to Catphish API:", {
    external_user_id: external_user_id,
    isEnrollment: isEnrollment,
    api_url: API_URL,
    api_key: API_KEY ? '***' : 'NOT_SET'
  });

  // Simulate API call delay
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simulate different scenarios for demo
      const random = Math.random();
      
      // 80% success rate for demo
      if (random > 0.2) {
        // Success - enroll user if needed
        if (isEnrollment) {
          const enrolledUsers = JSON.parse(localStorage.getItem('enrolled_users') || '[]');
          if (!enrolledUsers.includes(external_user_id)) {
            enrolledUsers.push(external_user_id);
            localStorage.setItem('enrolled_users', JSON.stringify(enrolledUsers));
          }
        }
        
        resolve({
          status: 200,
          session_id: `demo_session_${Date.now()}`,
          message: "Verification successful"
        });
      } else {
        // Failure
        resolve({
          status: 401,
          message: "Voice verification failed"
        });
      }
    }, 2000); // 2 second delay to simulate processing
  });
}

/**
 * When implementing the real API, replace the above with:
 * 
 * export async function checkUserEnrollment(external_user_id) {
 *   const response = await fetch(`${API_URL}/enrollment/status`, {
 *     method: 'POST',
 *     headers: {
 *       'Content-Type': 'application/json',
 *       'Authorization': `Bearer ${API_KEY}`
 *     },
 *     body: JSON.stringify({ external_user_id })
 *   });
 *   
 *   const data = await response.json();
 *   return {
 *     enrolled: data.enrolled,
 *     phrase: data.phrase
 *   };
 * }
 * 
 * export async function createVerificationSession(external_user_id, isEnrollment) {
 *   const endpoint = isEnrollment ? '/enroll' : '/verify';
 *   const response = await fetch(`${API_URL}${endpoint}`, {
 *     method: 'POST',
 *     headers: {
 *       'Content-Type': 'application/json',
 *       'Authorization': `Bearer ${API_KEY}`
 *     },
 *     body: JSON.stringify({ 
 *       external_user_id,
 *       // In real implementation, send audio data here
 *       audio_data: audioBlob
 *     })
 *   });
 *   
 *   const data = await response.json();
 *   return {
 *     status: response.status,
 *     session_id: data.session_id,
 *     message: data.message
 *   };
 * }
 */
