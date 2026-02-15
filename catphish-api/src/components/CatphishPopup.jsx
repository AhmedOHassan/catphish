import React, { useState, useEffect } from 'react';
import { enroll, createChallenge, verify } from '../services/catphishClient';
import { 
  requestMicrophonePermission, 
  recordAudio, 
  convertToWav, 
  blobToBase64,
  stopStream 
} from '../services/audioRecorder';

/**
 * CatphishPopup - Voice Verification Modal Component
 * 
 * This component handles the complete voice verification flow:
 * 1. Request microphone permission
 * 2. Record enrollment sample (3-5s)
 * 3. Submit enrollment
 * 4. Create challenge
 * 5. Record challenge response
 * 6. Verify and show results
 * 
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether popup is open
 * @param {Function} props.onClose - Callback when popup closes
 * @param {string} props.externalUserId - User ID from your system
 * @param {string} props.apiBaseUrl - Catphish API base URL (default: http://127.0.0.1:8000)
 * @param {string} props.apiKey - X-Catphish-Key header value
 * @param {string} props.mode - Optional mode: "enroll" | "challenge" (auto-detects if not provided)
 */
function CatphishPopup({ 
  isOpen, 
  onClose, 
  externalUserId, 
  apiBaseUrl = import.meta.env.VITE_CATPHISH_API_URL || 'http://127.0.0.1:8000',
  apiKey = import.meta.env.VITE_CATPHISH_API_KEY || 'demo_key_123',
  mode = null 
}) {
  // Step tracking
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  
  // Microphone state
  const [micPermission, setMicPermission] = useState('prompt'); // 'prompt' | 'granted' | 'denied'
  const [mediaStream, setMediaStream] = useState(null);
  
  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingProgress, setRecordingProgress] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  
  // Challenge state
  const [challengeId, setChallengeId] = useState(null);
  const [phrase, setPhrase] = useState('');
  const [expiresInSeconds, setExpiresInSeconds] = useState(0);
  
  // Result state
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Step definitions
  const STEPS = {
    MIC_PERMISSION: 0,
    ENROLL_RECORD: 1,
    ENROLL_SUBMIT: 2,
    CHALLENGE_CREATE: 3,
    CHALLENGE_RECORD: 4,
    VERIFY: 5,
    RESULT: 6,
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (mediaStream) {
        stopStream(mediaStream);
      }
    };
  }, [mediaStream]);

  // Request microphone permission
  const handleRequestMic = async () => {
    try {
      setError(null);
      const stream = await requestMicrophonePermission();
      setMediaStream(stream);
      setMicPermission('granted');
      setCurrentStep(STEPS.ENROLL_RECORD);
    } catch (err) {
      setError(err.message);
      setMicPermission('denied');
    }
  };

  // Record audio (enrollment or challenge)
  const handleRecord = async (duration = 5000) => {
    try {
      setError(null);
      setIsRecording(true);
      setRecordingProgress(0);
      
      // Progress animation
      const interval = setInterval(() => {
        setRecordingProgress(prev => {
          const next = prev + (100 / (duration / 100));
          return next >= 100 ? 100 : next;
        });
      }, 100);

      // Record audio
      const blob = await recordAudio(mediaStream, duration);
      
      clearInterval(interval);
      setIsRecording(false);
      setRecordingProgress(100);
      setAudioBlob(blob);
      
    } catch (err) {
      setError(`Recording failed: ${err.message}`);
      setIsRecording(false);
    }
  };

  // Submit enrollment
  const handleEnrollSubmit = async () => {
    if (!audioBlob) {
      setError('No recording available. Please record first.');
      return;
    }

    try {
      setError(null);
      setIsProcessing(true);

      // Convert to WAV and base64
      const wavBlob = await convertToWav(audioBlob);
      const base64Audio = await blobToBase64(wavBlob);

      // Call enrollment API
      const enrollResult = await enroll({
        external_user_id: externalUserId,
        audio_sample_base64: base64Audio,
        metadata: { source: 'popup' },
        apiBaseUrl,
        apiKey,
      });

      console.log('Enrollment successful:', enrollResult);
      
      // Move to challenge creation
      setCurrentStep(STEPS.CHALLENGE_CREATE);
      setAudioBlob(null); // Clear for next recording
      
    } catch (err) {
      setError(`Enrollment failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Create challenge
  const handleCreateChallenge = async () => {
    try {
      setError(null);
      setIsProcessing(true);

      const challengeResult = await createChallenge({
        external_user_id: externalUserId,
        purpose: 'login',
        ttl_seconds: 120,
        apiBaseUrl,
        apiKey,
      });

      setChallengeId(challengeResult.challenge_id);
      setPhrase(challengeResult.phrase);
      setExpiresInSeconds(challengeResult.expires_in_seconds);
      
      setCurrentStep(STEPS.CHALLENGE_RECORD);
      
    } catch (err) {
      setError(`Challenge creation failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Submit verification
  const handleVerifySubmit = async () => {
    if (!audioBlob) {
      setError('No recording available. Please record first.');
      return;
    }

    try {
      setError(null);
      setIsProcessing(true);

      // Convert to WAV and base64
      const wavBlob = await convertToWav(audioBlob);
      const base64Audio = await blobToBase64(wavBlob);

      // Call verify API
      const verifyResult = await verify({
        challenge_id: challengeId,
        external_user_id: externalUserId,
        audio_sample_base64: base64Audio,
        apiBaseUrl,
        apiKey,
      });

      setResult(verifyResult);
      setCurrentStep(STEPS.RESULT);
      
    } catch (err) {
      setError(`Verification failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Render step content
  const renderStep = () => {
    switch (currentStep) {
      case STEPS.MIC_PERMISSION:
        return (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>🎤 Microphone Access</h2>
            <p style={styles.stepDescription}>
              Catphish needs access to your microphone to verify your voice.
            </p>
            <button 
              style={styles.primaryButton} 
              onClick={handleRequestMic}
            >
              Allow Microphone
            </button>
            {micPermission === 'denied' && (
              <div style={styles.errorBox}>
                ⚠️ Microphone access denied. Please enable it in your browser settings.
              </div>
            )}
          </div>
        );

      case STEPS.ENROLL_RECORD:
        return (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>📝 Voice Enrollment</h2>
            <p style={styles.stepDescription}>
              Record a 3-5 second voice sample. Say anything you like!
            </p>
            {!audioBlob && !isRecording && (
              <button 
                style={styles.recordButton} 
                onClick={() => handleRecord(5000)}
              >
                🎤 Start Recording (5s)
              </button>
            )}
            {isRecording && (
              <div style={styles.recordingIndicator}>
                <div style={styles.recordingDot}></div>
                <p style={styles.recordingText}>Recording... Speak now!</p>
                <div style={styles.progressBar}>
                  <div 
                    style={{...styles.progressFill, width: `${recordingProgress}%`}}
                  ></div>
                </div>
              </div>
            )}
            {audioBlob && !isRecording && (
              <div style={styles.completedBox}>
                <p style={styles.completedText}>✓ Recording complete!</p>
                <div style={styles.buttonRow}>
                  <button 
                    style={styles.secondaryButton} 
                    onClick={() => setAudioBlob(null)}
                  >
                    🔄 Re-record
                  </button>
                  <button 
                    style={styles.primaryButton} 
                    onClick={() => setCurrentStep(STEPS.ENROLL_SUBMIT)}
                  >
                    Next →
                  </button>
                </div>
              </div>
            )}
          </div>
        );

      case STEPS.ENROLL_SUBMIT:
        return (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>✅ Submit Enrollment</h2>
            <p style={styles.stepDescription}>
              Ready to enroll your voice sample?
            </p>
            <button 
              style={styles.primaryButton} 
              onClick={handleEnrollSubmit}
              disabled={isProcessing}
            >
              {isProcessing ? 'Enrolling...' : 'Submit Enrollment'}
            </button>
            <button 
              style={styles.secondaryButton} 
              onClick={() => setCurrentStep(STEPS.ENROLL_RECORD)}
              disabled={isProcessing}
            >
              ← Back
            </button>
          </div>
        );

      case STEPS.CHALLENGE_CREATE:
        return (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>🎯 Create Challenge</h2>
            <p style={styles.stepDescription}>
              Enrollment successful! Now let's verify your voice.
            </p>
            <button 
              style={styles.primaryButton} 
              onClick={handleCreateChallenge}
              disabled={isProcessing}
            >
              {isProcessing ? 'Creating...' : 'Create Challenge'}
            </button>
          </div>
        );

      case STEPS.CHALLENGE_RECORD:
        return (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>🗣️ Speak the Phrase</h2>
            <div style={styles.phraseBox}>
              <p style={styles.phrase}>"{phrase}"</p>
            </div>
            <p style={styles.stepDescription}>
              Record yourself saying this phrase clearly.
            </p>
            {!audioBlob && !isRecording && (
              <button 
                style={styles.recordButton} 
                onClick={() => handleRecord(5000)}
              >
                🎤 Start Recording (5s)
              </button>
            )}
            {isRecording && (
              <div style={styles.recordingIndicator}>
                <div style={styles.recordingDot}></div>
                <p style={styles.recordingText}>Recording... Say the phrase!</p>
                <div style={styles.progressBar}>
                  <div 
                    style={{...styles.progressFill, width: `${recordingProgress}%`}}
                  ></div>
                </div>
              </div>
            )}
            {audioBlob && !isRecording && (
              <div style={styles.completedBox}>
                <p style={styles.completedText}>✓ Recording complete!</p>
                <div style={styles.buttonRow}>
                  <button 
                    style={styles.secondaryButton} 
                    onClick={() => setAudioBlob(null)}
                  >
                    🔄 Re-record
                  </button>
                  <button 
                    style={styles.primaryButton} 
                    onClick={() => setCurrentStep(STEPS.VERIFY)}
                  >
                    Next →
                  </button>
                </div>
              </div>
            )}
            <div style={styles.infoBox}>
              ⏱️ Challenge expires in {expiresInSeconds} seconds
            </div>
          </div>
        );

      case STEPS.VERIFY:
        return (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>🔍 Verify Voice</h2>
            <p style={styles.stepDescription}>
              Ready to verify your recording?
            </p>
            <button 
              style={styles.primaryButton} 
              onClick={handleVerifySubmit}
              disabled={isProcessing}
            >
              {isProcessing ? 'Verifying...' : 'Verify Now'}
            </button>
            <button 
              style={styles.secondaryButton} 
              onClick={() => setCurrentStep(STEPS.CHALLENGE_RECORD)}
              disabled={isProcessing}
            >
              ← Back
            </button>
          </div>
        );

      case STEPS.RESULT:
        if (!result) return null;
        
        const isSuccess = result.status === 'verified';
        const statusIcon = isSuccess ? '✅' : '❌';
        const statusText = isSuccess ? 'VERIFIED' : 'FAILED';
        const statusColor = isSuccess ? '#4CAF50' : '#f44336';

        return (
          <div style={styles.stepContent}>
            <h2 style={{...styles.stepTitle, color: statusColor}}>
              {statusIcon} {statusText}
            </h2>
            
            <div style={styles.resultGrid}>
              <div style={styles.resultItem}>
                <span style={styles.resultLabel}>Status:</span>
                <span style={{...styles.resultValue, color: statusColor}}>
                  {result.status}
                </span>
              </div>
              
              <div style={styles.resultItem}>
                <span style={styles.resultLabel}>Confidence:</span>
                <span style={styles.resultValue}>
                  {(result.confidence_score * 100).toFixed(1)}%
                </span>
              </div>
              
              {result.similarity !== null && (
                <div style={styles.resultItem}>
                  <span style={styles.resultLabel}>Similarity:</span>
                  <span style={styles.resultValue}>
                    {(result.similarity * 100).toFixed(1)}%
                  </span>
                </div>
              )}
              
              {result.ai_probability !== null && (
                <div style={styles.resultItem}>
                  <span style={styles.resultLabel}>AI Probability:</span>
                  <span style={styles.resultValue}>
                    {(result.ai_probability * 100).toFixed(1)}%
                  </span>
                </div>
              )}
              
              <div style={styles.resultItem}>
                <span style={styles.resultLabel}>Risk Level:</span>
                <span style={styles.resultValue}>
                  {result.risk_level}
                </span>
              </div>
            </div>

            {result.reasons && result.reasons.length > 0 && (
              <div style={styles.reasonsBox}>
                <p style={styles.reasonsTitle}>Details:</p>
                <ul style={styles.reasonsList}>
                  {result.reasons.map((reason, idx) => (
                    <li key={idx} style={styles.reasonItem}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            <button 
              style={styles.primaryButton} 
              onClick={onClose}
            >
              Close
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  if (!isOpen) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <button style={styles.closeButton} onClick={onClose}>×</button>
        
        {error && (
          <div style={styles.errorBox}>
            ⚠️ {error}
          </div>
        )}

        {renderStep()}

        {isProcessing && (
          <div style={styles.processingOverlay}>
            <div style={styles.spinner}></div>
            <p>Processing...</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Styles
const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10000,
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '30px',
    maxWidth: '600px',
    width: '90%',
    maxHeight: '90vh',
    overflow: 'auto',
    position: 'relative',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
  },
  closeButton: {
    position: 'absolute',
    top: '15px',
    right: '15px',
    fontSize: '30px',
    border: 'none',
    background: 'none',
    cursor: 'pointer',
    color: '#666',
    padding: '0',
    width: '40px',
    height: '40px',
    lineHeight: '40px',
    textAlign: 'center',
  },
  stepContent: {
    padding: '20px 0',
  },
  stepTitle: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '15px',
    textAlign: 'center',
  },
  stepDescription: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '25px',
    textAlign: 'center',
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
    color: 'white',
    fontSize: '18px',
    fontWeight: 'bold',
    padding: '15px 40px',
    border: 'none',
    borderRadius: '25px',
    cursor: 'pointer',
    width: '100%',
    marginBottom: '10px',
    transition: 'background-color 0.3s',
  },
  secondaryButton: {
    backgroundColor: '#95a5a6',
    color: 'white',
    fontSize: '16px',
    padding: '12px 30px',
    border: 'none',
    borderRadius: '25px',
    cursor: 'pointer',
    width: '100%',
    transition: 'background-color 0.3s',
  },
  recordButton: {
    backgroundColor: '#e74c3c',
    color: 'white',
    fontSize: '20px',
    fontWeight: 'bold',
    padding: '20px 40px',
    border: 'none',
    borderRadius: '50px',
    cursor: 'pointer',
    width: '100%',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  },
  recordingIndicator: {
    padding: '20px',
    backgroundColor: '#ffebee',
    borderRadius: '8px',
    textAlign: 'center',
  },
  recordingDot: {
    width: '20px',
    height: '20px',
    backgroundColor: '#e74c3c',
    borderRadius: '50%',
    margin: '0 auto 10px',
    animation: 'pulse 1.5s ease-in-out infinite',
  },
  recordingText: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#e74c3c',
    margin: '10px 0',
  },
  progressBar: {
    width: '100%',
    height: '8px',
    backgroundColor: '#ddd',
    borderRadius: '4px',
    overflow: 'hidden',
    marginTop: '15px',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#e74c3c',
    transition: 'width 0.1s linear',
  },
  completedBox: {
    backgroundColor: '#d4edda',
    padding: '20px',
    borderRadius: '8px',
  },
  completedText: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#155724',
    textAlign: 'center',
    marginBottom: '15px',
  },
  buttonRow: {
    display: 'flex',
    gap: '10px',
  },
  phraseBox: {
    backgroundColor: '#f0f8ff',
    border: '2px solid #4CAF50',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
  },
  phrase: {
    fontSize: '22px',
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
    fontStyle: 'italic',
    margin: 0,
  },
  infoBox: {
    marginTop: '15px',
    padding: '12px',
    backgroundColor: '#f8f9fa',
    borderRadius: '6px',
    borderLeft: '4px solid #3498db',
    fontSize: '14px',
    color: '#666',
  },
  errorBox: {
    backgroundColor: '#ffebee',
    color: '#c62828',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
    border: '1px solid #ef5350',
  },
  resultGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '15px',
    marginBottom: '20px',
  },
  resultItem: {
    backgroundColor: '#f5f5f5',
    padding: '15px',
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
  },
  resultLabel: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '5px',
  },
  resultValue: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#333',
  },
  reasonsBox: {
    backgroundColor: '#fff3cd',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  reasonsTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '10px',
  },
  reasonsList: {
    marginLeft: '20px',
    marginBottom: '0',
  },
  reasonItem: {
    marginBottom: '5px',
    fontSize: '14px',
  },
  processingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: '12px',
  },
  spinner: {
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #3498db',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    animation: 'spin 1s linear infinite',
    marginBottom: '15px',
  },
};

// Add CSS animations
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
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
}

export default CatphishPopup;
