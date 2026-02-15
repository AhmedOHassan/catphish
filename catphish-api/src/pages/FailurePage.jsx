import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function FailurePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const result = location.state?.result || {};
  const errorMessage = location.state?.error || '';

  // Build dynamic reasons from the backend response
  const backendReasons = result.reasons || [];
  const displayReasons = backendReasons.length > 0
    ? backendReasons
    : [
        'Background noise interfering with recording',
        'Voice doesn\'t match stored biometric',
        'Poor audio quality or microphone issues',
        'Incorrect phrase spoken',
      ];

  const handleRetry = () => {
    // Go back to verification page with the same session to retry
    const sid = location.state?.sessionId;
    if (sid) {
      navigate(`/verify?session_id=${sid}`);
    } else {
      // No session available — redirect to parent app to start fresh
      const returnUrl = localStorage.getItem('catphish_return_url');
      if (returnUrl) {
        localStorage.removeItem('catphish_return_url');
        window.location.href = returnUrl;
      } else {
        window.location.href = 'http://localhost:3000/login';
      }
    }
  };

  const handleReturnToApp = () => {
    // Clean up
    localStorage.removeItem('catphish_return_url');
    localStorage.removeItem('pending_login_user');
    
    // Go straight to login page
    window.location.href = 'http://localhost:3000/login';
  };

  const handleGoHome = () => {
    // Check if we should return to parent app
    const returnUrl = localStorage.getItem('catphish_return_url');
    if (returnUrl) {
      handleReturnToApp();
    } else {
      window.location.href = '/';
    }
  };

  const handleContactSupport = () => {
    // In a real app, this would open a support ticket or contact form
    alert('In a production app, this would open a support contact form or help center.');
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.iconContainer}>
          <div style={styles.failureIcon}>✕</div>
        </div>
        
        <h1 style={styles.title}>Verification Failed</h1>
        
        <p style={styles.message}>
          {result.message || errorMessage || "We couldn't verify your voice. This could be due to several reasons:"}
        </p>

        <div style={styles.reasonsBox}>
          <ul style={styles.reasonsList}>
            {displayReasons.map((reason, i) => (
              <li key={i} style={styles.reasonItem}>{reason}</li>
            ))}
          </ul>
        </div>

        <div style={styles.detailsBox}>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>Status:</span>
            <span style={styles.detailValue}>❌ {result.status || 'Failed'}</span>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>Timestamp:</span>
            <span style={styles.detailValue}>{new Date().toLocaleString()}</span>
          </div>
          {result.ai_probability != null && (
            <div style={styles.detailRow}>
              <span style={styles.detailLabel}>AI Probability:</span>
              <span style={styles.detailValue}>{(result.ai_probability * 100).toFixed(1)}%</span>
            </div>
          )}
          {result.similarity != null && (
            <div style={styles.detailRow}>
              <span style={styles.detailLabel}>Voice Similarity:</span>
              <span style={styles.detailValue}>{(result.similarity * 100).toFixed(1)}%</span>
            </div>
          )}
        </div>

        <div style={styles.buttonContainer}>
          <button 
            onClick={handleRetry}
            style={styles.retryButton}
          >
            🔄 Try Again
          </button>
          
          <button 
            onClick={handleReturnToApp}
            style={styles.homeButton}
          >
            ← Return to Login
          </button>
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
    textAlign: 'center',
  },
  iconContainer: {
    marginBottom: '20px',
  },
  failureIcon: {
    display: 'inline-flex',
    justifyContent: 'center',
    alignItems: 'center',
    width: '100px',
    height: '100px',
    backgroundColor: '#e74c3c',
    color: 'white',
    fontSize: '60px',
    borderRadius: '50%',
    fontWeight: 'bold',
    boxShadow: '0 4px 12px rgba(231, 76, 60, 0.3)',
  },
  title: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: '20px',
  },
  message: {
    fontSize: '18px',
    color: '#555',
    marginBottom: '20px',
    lineHeight: '1.5',
  },
  reasonsBox: {
    backgroundColor: '#fff3cd',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
    textAlign: 'left',
    border: '1px solid #ffc107',
  },
  reasonsList: {
    margin: 0,
    paddingLeft: '20px',
  },
  reasonItem: {
    fontSize: '15px',
    color: '#856404',
    marginBottom: '8px',
    lineHeight: '1.4',
  },
  detailsBox: {
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '30px',
    textAlign: 'left',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px 0',
    borderBottom: '1px solid #e0e0e0',
  },
  detailLabel: {
    fontWeight: 'bold',
    color: '#666',
  },
  detailValue: {
    color: '#333',
  },
  buttonContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    marginBottom: '20px',
  },
  retryButton: {
    backgroundColor: '#3498db',
    color: 'white',
    fontSize: '18px',
    fontWeight: 'bold',
    padding: '15px 40px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  supportButton: {
    backgroundColor: '#9b59b6',
    color: 'white',
    fontSize: '16px',
    padding: '12px 30px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  homeButton: {
    backgroundColor: '#6c757d',
    color: 'white',
    fontSize: '16px',
    padding: '12px 30px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  warningBox: {
    padding: '15px',
    backgroundColor: '#ffebee',
    borderRadius: '8px',
    borderLeft: '4px solid #e74c3c',
  },
  warningText: {
    fontSize: '14px',
    color: '#c62828',
    margin: 0,
  },
};

export default FailurePage;
