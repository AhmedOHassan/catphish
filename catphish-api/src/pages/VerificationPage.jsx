import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkUserEnrollment, createVerificationSession } from '../services/catphishService';

function VerificationPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [phrase, setPhrase] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [hasRecorded, setHasRecorded] = useState(false);
  const [externalUserId, setExternalUserId] = useState('');

  useEffect(() => {
    // Get external_user_id from URL parameters (passed from parent app)
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromUrl = urlParams.get('user_id');
    const returnUrlFromUrl = urlParams.get('return_url');
    
    let userId = userIdFromUrl;
    
    if (!userId) {
      // Fallback: try localStorage (for backward compatibility)
      userId = localStorage.getItem('external_user_id');
    }
    
    if (!userId) {
      // If still no user ID, create a demo one
      const demoUserId = `user_${Date.now()}`;
      userId = demoUserId;
    }
    
    // Store in localStorage for this session
    localStorage.setItem('external_user_id', userId);
    setExternalUserId(userId);
    
    // Store return URL if provided
    if (returnUrlFromUrl) {
      localStorage.setItem('catphish_return_url', returnUrlFromUrl);
    }

    // Check if user is enrolled
    checkEnrollmentStatus(userId);
  }, []);

  const checkEnrollmentStatus = async (userId) => {
    try {
      setLoading(true);
      const result = await checkUserEnrollment(userId);
      setIsEnrolled(result.enrolled);
      setPhrase(result.phrase);
    } catch (error) {
      console.error('Error checking enrollment:', error);
      // Default to enrollment flow on error
      setIsEnrolled(false);
      setPhrase("Silver tiger 42 jumps quickly");
    } finally {
      setLoading(false);
    }
  };

  const handleRecord = () => {
    // Simulate recording audio
    setIsRecording(true);
    
    // TODO: In real implementation, capture audio from microphone
    // const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    // const mediaRecorder = new MediaRecorder(stream);
    
    // Simulate recording for 3 seconds
    setTimeout(() => {
      setIsRecording(false);
      setHasRecorded(true);
      console.log('🎤 Recording complete (simulated)');
    }, 3000);
  };

  const handleVerify = async () => {
    if (!hasRecorded) {
      alert('Please record your voice first');
      return;
    }

    try {
      setIsVerifying(true);
      
      // TODO: In real implementation, send the actual audio recording
      // For now, we just send the user ID
      const result = await createVerificationSession(externalUserId, !isEnrolled);
      
      console.log('Verification result:', result);
      
      // Handle response based on status code
      if (result.status === 200) {
        // Success - redirect to success page
        navigate('/success');
      } else if (result.status === 401) {
        // Failure - redirect to failure page
        navigate('/failure');
      } else {
        // Other errors
        alert('An error occurred during verification');
      }
    } catch (error) {
      console.error('Verification error:', error);
      navigate('/failure');
    } finally {
      setIsVerifying(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>
          {isEnrolled ? '🔐 Voice Verification' : '🎤 Voice Enrollment'}
        </h1>
        
        <div style={styles.messageBox}>
          {isEnrolled ? (
            <>
              <p style={styles.message}>
                User already enrolled. Please verify your identity.
              </p>
              <p style={styles.subtitle}>Say the following phrase:</p>
            </>
          ) : (
            <>
              <p style={styles.message}>
                To protect your account, please record your voice.
              </p>
              <p style={styles.subtitle}>Say the following phrase:</p>
            </>
          )}
          
          <div style={styles.phraseBox}>
            <p style={styles.phrase}>"{phrase}"</p>
          </div>
        </div>

        <div style={styles.buttonContainer}>
          {!hasRecorded && !isRecording && (
            <button 
              onClick={handleRecord}
              style={styles.recordButton}
              disabled={isRecording || isVerifying}
            >
              🎤 Start Recording
            </button>
          )}

          {isRecording && (
            <div style={styles.recordingIndicator}>
              <div style={styles.recordingDot}></div>
              <p style={styles.recordingText}>Recording... Speak now</p>
            </div>
          )}

          {hasRecorded && !isRecording && (
            <>
              <div style={styles.successMessage}>
                ✓ Recording complete!
              </div>
              <button 
                onClick={handleVerify}
                style={styles.verifyButton}
                disabled={isVerifying}
              >
                {isVerifying ? (
                  <>
                    <span style={styles.spinner}></span>
                    Verifying...
                  </>
                ) : (
                  isEnrolled ? '🔍 Verify Voice' : '✓ Submit Enrollment'
                )}
              </button>
              <button 
                onClick={() => {
                  setHasRecorded(false);
                  setIsRecording(false);
                }}
                style={styles.retryButton}
                disabled={isVerifying}
              >
                🔄 Re-record
              </button>
            </>
          )}
        </div>

        <div style={styles.infoBox}>
          <p style={styles.infoText}>
            ℹ️ User ID: {externalUserId}
          </p>
          <p style={styles.infoText}>
            {isEnrolled ? 'Enrolled User - Verification Flow' : 'New User - Enrollment Flow'}
          </p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '40px',
    maxWidth: '600px',
    width: '100%',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: '30px',
    color: '#333',
  },
  messageBox: {
    marginBottom: '30px',
  },
  message: {
    fontSize: '18px',
    color: '#555',
    textAlign: 'center',
    marginBottom: '15px',
  },
  subtitle: {
    fontSize: '16px',
    color: '#777',
    textAlign: 'center',
    marginBottom: '10px',
  },
  phraseBox: {
    backgroundColor: '#f0f8ff',
    border: '2px solid #4CAF50',
    borderRadius: '8px',
    padding: '20px',
    marginTop: '15px',
  },
  phrase: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
    fontStyle: 'italic',
    margin: 0,
  },
  buttonContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    alignItems: 'center',
    marginTop: '30px',
  },
  recordButton: {
    backgroundColor: '#e74c3c',
    color: 'white',
    fontSize: '20px',
    fontWeight: 'bold',
    padding: '20px 50px',
    border: 'none',
    borderRadius: '50px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  verifyButton: {
    backgroundColor: '#4CAF50',
    color: 'white',
    fontSize: '20px',
    fontWeight: 'bold',
    padding: '20px 50px',
    border: 'none',
    borderRadius: '50px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  retryButton: {
    backgroundColor: '#95a5a6',
    color: 'white',
    fontSize: '16px',
    padding: '12px 30px',
    border: 'none',
    borderRadius: '25px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  recordingIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '20px',
    backgroundColor: '#ffebee',
    borderRadius: '8px',
  },
  recordingDot: {
    width: '20px',
    height: '20px',
    backgroundColor: '#e74c3c',
    borderRadius: '50%',
    animation: 'pulse 1.5s ease-in-out infinite',
  },
  recordingText: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#e74c3c',
    margin: 0,
  },
  successMessage: {
    backgroundColor: '#d4edda',
    color: '#155724',
    padding: '15px 30px',
    borderRadius: '8px',
    fontSize: '18px',
    fontWeight: 'bold',
  },
  infoBox: {
    marginTop: '30px',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    borderLeft: '4px solid #3498db',
  },
  infoText: {
    fontSize: '14px',
    color: '#666',
    margin: '5px 0',
  },
  loadingText: {
    fontSize: '18px',
    color: '#666',
    textAlign: 'center',
    marginTop: '20px',
  },
  spinner: {
    border: '3px solid #f3f3f3',
    borderTop: '3px solid #3498db',
    borderRadius: '50%',
    width: '40px',
    height: '40px',
    animation: 'spin 1s linear infinite',
    margin: '0 auto',
  },
};

// Add CSS animations
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.2); }
  }
`;
document.head.appendChild(styleSheet);

export default VerificationPage;
