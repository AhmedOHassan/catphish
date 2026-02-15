import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSessionStatus, enrollVoice, verifyVoice } from '../services/catphishService';
import useAudioRecorder from '../hooks/useAudioRecorder';

function VerificationPage() {
  const navigate = useNavigate();

  // Session state
  const [loading, setLoading] = useState(true);
  const [sessionId, setSessionId] = useState('');
  const [externalUserId, setExternalUserId] = useState('');
  const [returnUrl, setReturnUrl] = useState('');
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [phrase, setPhrase] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Processing state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  // Audio recorder hook
  const {
    isRecording,
    audioBase64,
    error: micError,
    recordingTime,
    startRecording,
    stopRecording,
    reset: resetAudio,
  } = useAudioRecorder();

  // ── On mount: read session_id from URL, fetch session status ──
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sid = params.get('session_id');
    if (!sid) {
      setErrorMsg('Invalid verification link — missing session_id.');
      setLoading(false);
      return;
    }
    setSessionId(sid);
    loadSession(sid);
  }, []);

  const loadSession = async (sid) => {
    try {
      setLoading(true);
      const data = await getSessionStatus(sid);
      setExternalUserId(data.external_user_id);
      setReturnUrl(data.return_url || '');
      setIsEnrolled(data.enrolled);
      setPhrase(data.phrase);

      // Store return_url so Success/Failure pages can use it
      if (data.return_url) {
        localStorage.setItem('catphish_return_url', data.return_url);
      }
    } catch (err) {
      console.error('Session load error:', err);
      setErrorMsg('Failed to load verification session. It may have expired.');
    } finally {
      setLoading(false);
    }
  };

  // ── Submit audio to backend ──
  const handleSubmit = async () => {
    if (!audioBase64) return;

    setIsSubmitting(true);
    setStatusMessage(isEnrolled ? 'Verifying your voice...' : 'Enrolling your voice...');

    try {
      if (isEnrolled) {
        // Returning user → verify
        const result = await verifyVoice(sessionId, audioBase64);
        if (result.status === 'verified') {
          navigate('/success', { state: { result } });
        } else {
          navigate('/failure', { state: { result } });
        }
      } else {
        // New user → enroll
        const result = await enrollVoice(sessionId, audioBase64);
        if (result.success) {
          navigate('/success', { state: { result, enrollment: true } });
        } else {
          navigate('/failure', { state: { result } });
        }
      }
    } catch (err) {
      console.error('Submit error:', err);
      navigate('/failure', { state: { error: err.message } });
    } finally {
      setIsSubmitting(false);
      setStatusMessage('');
    }
  };

  // ── Re-record ──
  const handleReRecord = () => {
    resetAudio();
  };

  // ── Render helpers ──
  const formatTime = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  // ── Error state ──
  if (errorMsg) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={styles.errorIcon}>!</div>
          <h1 style={{ ...styles.title, color: '#e74c3c' }}>Session Error</h1>
          <p style={styles.message}>{errorMsg}</p>
        </div>
      </div>
    );
  }

  // ── Loading state ──
  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={styles.spinner} />
          <p style={styles.loadingText}>Loading verification session...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {/* Header */}
        <h1 style={styles.title}>
          {isEnrolled ? '🔐 Voice Verification' : '🎤 Voice Enrollment'}
        </h1>

        <div style={styles.messageBox}>
          <p style={styles.message}>
            {isEnrolled
              ? 'Welcome back! Please verify your identity by saying the phrase below.'
              : 'To protect your account from AI voice fraud, please say the following phrase:'}
          </p>

          <div style={styles.phraseBox}>
            <p style={styles.phrase}>"{phrase}"</p>
          </div>
        </div>

        {/* Microphone error */}
        {micError && (
          <div style={styles.micError}>
            <p>⚠️ {micError}</p>
          </div>
        )}

        {/* Controls */}
        <div style={styles.buttonContainer}>
          {/* State 1: Not recorded yet, not recording */}
          {!audioBase64 && !isRecording && (
            <button onClick={startRecording} style={styles.recordButton} disabled={isSubmitting}>
              🎤 Start Recording
            </button>
          )}

          {/* State 2: Recording in progress */}
          {isRecording && (
            <div style={styles.recordingContainer}>
              <div style={styles.recordingIndicator}>
                <div style={styles.recordingDot} />
                <p style={styles.recordingText}>Recording... {formatTime(recordingTime)}</p>
              </div>
              <button onClick={stopRecording} style={styles.stopButton}>
                ◼ Stop Recording
              </button>
            </div>
          )}

          {/* State 3: Recorded, ready to submit */}
          {audioBase64 && !isRecording && !isSubmitting && (
            <>
              <div style={styles.successMessage}>✓ Recording complete!</div>
              <button onClick={handleSubmit} style={styles.verifyButton}>
                {isEnrolled ? '🔍 Verify Voice' : '✓ Submit Enrollment'}
              </button>
              <button onClick={handleReRecord} style={styles.retryButton}>
                🔄 Re-record
              </button>
            </>
          )}

          {/* State 4: Submitting */}
          {isSubmitting && (
            <div style={styles.submittingContainer}>
              <div style={styles.spinner} />
              <p style={styles.loadingText}>{statusMessage}</p>
            </div>
          )}
        </div>

        {/* Info footer */}
        <div style={styles.infoBox}>
          <p style={styles.infoText}>Session: {sessionId}</p>
          <p style={styles.infoText}>User: {externalUserId}</p>
          <p style={styles.infoText}>
            {isEnrolled ? '🔁 Returning user — verification flow' : '🆕 New user — enrollment flow'}
          </p>
        </div>
      </div>
    </div>
  );
}

// ───────── Styles ─────────
const styles = {
  container: {
    display: 'flex', justifyContent: 'center', alignItems: 'center',
    minHeight: '100vh', backgroundColor: '#f5f5f5', padding: '20px',
  },
  card: {
    backgroundColor: 'white', borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)', padding: '40px',
    maxWidth: '600px', width: '100%',
  },
  title: {
    fontSize: '32px', fontWeight: 'bold', textAlign: 'center',
    marginBottom: '30px', color: '#333',
  },
  messageBox: { marginBottom: '30px' },
  message: {
    fontSize: '18px', color: '#555', textAlign: 'center', marginBottom: '15px',
  },
  phraseBox: {
    backgroundColor: '#f0f8ff', border: '2px solid #4CAF50',
    borderRadius: '8px', padding: '20px', marginTop: '15px',
  },
  phrase: {
    fontSize: '24px', fontWeight: 'bold', color: '#2c3e50',
    textAlign: 'center', fontStyle: 'italic', margin: 0,
  },
  buttonContainer: {
    display: 'flex', flexDirection: 'column', gap: '15px',
    alignItems: 'center', marginTop: '30px',
  },
  recordButton: {
    backgroundColor: '#e74c3c', color: 'white', fontSize: '20px',
    fontWeight: 'bold', padding: '20px 50px', border: 'none',
    borderRadius: '50px', cursor: 'pointer',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  },
  stopButton: {
    backgroundColor: '#c0392b', color: 'white', fontSize: '18px',
    fontWeight: 'bold', padding: '15px 40px', border: 'none',
    borderRadius: '50px', cursor: 'pointer', marginTop: '15px',
  },
  verifyButton: {
    backgroundColor: '#4CAF50', color: 'white', fontSize: '20px',
    fontWeight: 'bold', padding: '20px 50px', border: 'none',
    borderRadius: '50px', cursor: 'pointer',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  },
  retryButton: {
    backgroundColor: '#95a5a6', color: 'white', fontSize: '16px',
    padding: '12px 30px', border: 'none', borderRadius: '25px', cursor: 'pointer',
  },
  recordingContainer: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
  },
  recordingIndicator: {
    display: 'flex', alignItems: 'center', gap: '15px',
    padding: '20px', backgroundColor: '#ffebee', borderRadius: '8px',
  },
  recordingDot: {
    width: '20px', height: '20px', backgroundColor: '#e74c3c',
    borderRadius: '50%', animation: 'pulse 1.5s ease-in-out infinite',
  },
  recordingText: {
    fontSize: '18px', fontWeight: 'bold', color: '#e74c3c', margin: 0,
  },
  successMessage: {
    backgroundColor: '#d4edda', color: '#155724',
    padding: '15px 30px', borderRadius: '8px',
    fontSize: '18px', fontWeight: 'bold',
  },
  submittingContainer: {
    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '15px',
  },
  micError: {
    backgroundColor: '#f8d7da', color: '#721c24', padding: '12px 20px',
    borderRadius: '8px', marginBottom: '15px', textAlign: 'center',
  },
  errorIcon: {
    display: 'inline-flex', justifyContent: 'center', alignItems: 'center',
    width: '80px', height: '80px', backgroundColor: '#e74c3c', color: 'white',
    fontSize: '48px', borderRadius: '50%', fontWeight: 'bold', margin: '0 auto 20px',
  },
  infoBox: {
    marginTop: '30px', padding: '15px', backgroundColor: '#f8f9fa',
    borderRadius: '8px', borderLeft: '4px solid #3498db',
  },
  infoText: { fontSize: '14px', color: '#666', margin: '5px 0' },
  loadingText: { fontSize: '18px', color: '#666', textAlign: 'center', marginTop: '20px' },
  spinner: {
    border: '3px solid #f3f3f3', borderTop: '3px solid #3498db',
    borderRadius: '50%', width: '40px', height: '40px',
    animation: 'spin 1s linear infinite', margin: '0 auto',
  },
};

// CSS animations
if (typeof document !== 'undefined') {
  const id = 'catphish-animations';
  if (!document.getElementById(id)) {
    const s = document.createElement('style');
    s.id = id;
    s.textContent = `
      @keyframes spin { 0%{transform:rotate(0)} 100%{transform:rotate(360deg)} }
      @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.2)} }
    `;
    document.head.appendChild(s);
  }
}

export default VerificationPage;
