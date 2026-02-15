import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { login, setCurrentUser } from '../services/authService';
import Navbar from '../components/Navbar';
// Import CatphishPopup component from catphish-api
import CatphishPopup from '../../../catphish-api/src/components/CatphishPopup';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  
  // Catphish popup state
  const [showPopup, setShowPopup] = useState(false);
  const [userId, setUserId] = useState(null);
  
  // API configuration from environment variables
  const apiBaseUrl = import.meta.env.VITE_CATPHISH_API_URL || 'http://127.0.0.1:8000';
  const apiKey = import.meta.env.VITE_CATPHISH_API_KEY || 'demo_key_123';

  useEffect(() => {
    // Show success message if redirected from signup
    if (location.state?.message) {
      setSuccess(location.state.message);
    }
  }, [location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    // Validate inputs
    if (!email || !password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    // Login user
    const result = login(email, password);

    if (!result.success) {
      setError(result.message);
      setLoading(false);
      return;
    }

    // Login successful, now show Catphish popup
    setLoading(false);
    
    console.log('🔐 Login successful, opening Catphish verification popup...');
    
    // Save user data temporarily
    localStorage.setItem('pending_login_user', JSON.stringify(result.user));
    
    // Open the popup
    setUserId(result.user.id);
    setShowPopup(true);
  };

  // Handle popup close - called when verification completes or user cancels
  const handlePopupClose = () => {
    setShowPopup(false);
    setVerifying(false);
    
    // Check if verification was successful (we can add a callback prop to get result)
    // For now, we'll navigate to dashboard after popup closes
    const pendingUser = localStorage.getItem('pending_login_user');
    if (pendingUser) {
      const user = JSON.parse(pendingUser);
      setCurrentUser(user);
      localStorage.removeItem('pending_login_user');
      navigate('/dashboard');
    }
  };

  return (
    <div className="login-page">
      <Navbar 
        onLoginClick={() => navigate('/login')}
        onSignUpClick={() => navigate('/signup')}
      />
      
      <div className="auth-container">
        <div className="auth-card">
          <h1>Welcome Back</h1>
          <p className="subtitle">Log in to SecureBank</p>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          {verifying && (
            <div className="verifying-message">
              <div className="spinner"></div>
              <p>🎤 Redirecting to voice verification...</p>
              <p style={{fontSize: '14px', color: '#666'}}>You'll be redirected to complete voice verification</p>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
                disabled={verifying}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                disabled={verifying}
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading || verifying}>
              {loading ? 'Logging in...' : verifying ? 'Verifying...' : 'Login'}
            </button>
          </form>

          <p className="auth-footer">
            Don't have an account?{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/signup'); }}>
              Sign up
            </a>
          </p>
        </div>
      </div>

      {/* Catphish Popup */}
      <CatphishPopup
        isOpen={showPopup}
        onClose={handlePopupClose}
        externalUserId={userId}
        apiBaseUrl={apiBaseUrl}
        apiKey={apiKey}
      />
    </div>
  );
}

export default LoginPage;
