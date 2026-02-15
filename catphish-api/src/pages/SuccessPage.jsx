import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function SuccessPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const result = location.state?.result || {};
  const isEnrollment = location.state?.enrollment || false;

  useEffect(() => {
    // Auto-redirect after 3 seconds if return URL exists
    const returnUrl = localStorage.getItem('catphish_return_url');
    if (returnUrl) {
      const timer = setTimeout(() => {
        handleReturnToApp();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleReturnToApp = () => {
    const returnUrl = localStorage.getItem('catphish_return_url') || 'http://localhost:3000/dashboard';
    localStorage.removeItem('catphish_return_url');

    const url = new URL(returnUrl);
    url.searchParams.set('verification_status', 'success');
    window.location.href = url.toString();
  };

  const handleNewVerification = () => {
    // Start a new verification session
    navigate('/verify');
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

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.iconContainer}>
          <div style={styles.successIcon}>✓</div>
        </div>
        
        <h1 style={styles.title}>
          {isEnrollment ? 'Voice Enrolled!' : 'Voice Verified!'}
        </h1>
        
        <p style={styles.message}>
          {isEnrollment
            ? 'Your voice has been enrolled successfully. Your account is now protected.'
            : 'Your voice has been successfully verified. Access granted.'}
        </p>

        <div style={styles.detailsBox}>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>Status:</span>
            <span style={styles.detailValue}>✅ Verified</span>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>Timestamp:</span>
            <span style={styles.detailValue}>{new Date().toLocaleString()}</span>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>Session ID:</span>
            <span style={styles.detailValue}>demo_session_{Date.now()}</span>
          </div>
        </div>

        <div style={styles.buttonContainer}>
          <button 
            onClick={handleReturnToApp}
            style={styles.continueButton}
          >
            {localStorage.getItem('catphish_return_url') ? 'Continue to Application' : 'Continue'}
          </button>
          
          <button 
            onClick={handleNewVerification}
            style={styles.secondaryButton}
          >
            Start New Verification
          </button>
        </div>

        {localStorage.getItem('catphish_return_url') && (
          <p style={styles.autoRedirect}>Automatically redirecting in 2 seconds...</p>
        )}

        <div style={styles.infoBox}>
          <p style={styles.infoText}>
            🔒 Your voice biometric has been securely verified using Catphish technology.
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
    textAlign: 'center',
  },
  iconContainer: {
    marginBottom: '20px',
  },
  successIcon: {
    display: 'inline-flex',
    justifyContent: 'center',
    alignItems: 'center',
    width: '100px',
    height: '100px',
    backgroundColor: '#4CAF50',
    color: 'white',
    fontSize: '60px',
    borderRadius: '50%',
    fontWeight: 'bold',
    boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)',
  },
  title: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: '20px',
  },
  message: {
    fontSize: '20px',
    color: '#555',
    marginBottom: '30px',
    lineHeight: '1.5',
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
  continueButton: {
    backgroundColor: '#4CAF50',
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
  secondaryButton: {
    backgroundColor: '#6c757d',
    color: 'white',
    fontSize: '16px',
    padding: '12px 30px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  infoBox: {
    padding: '15px',
    backgroundColor: '#e3f2fd',
    borderRadius: '8px',
    borderLeft: '4px solid #2196F3',
  },
  infoText: {
    fontSize: '14px',
    color: '#1565c0',
    margin: 0,
  },
  autoRedirect: {
    fontSize: '14px',
    color: '#666',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: '15px',
  },
};

export default SuccessPage;
