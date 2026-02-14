import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { login, setCurrentUser } from '../services/authService';
import { createVerificationSession } from '../services/catphishService';
import Navbar from '../components/Navbar';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);

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

    // Login successful, now call Catphish API
    setLoading(false);
    setVerifying(true);

    try {
      console.log('🔐 Login successful, calling Catphish API...');
      const response = await createVerificationSession(result.user.id);

      if (response.status === 200) {
        // Verification successful
        console.log('✅ Verification successful!');
        setCurrentUser(result.user);
        navigate('/dashboard');
      } else {
        // Verification failed
        console.log('❌ Verification failed');
        setError('Voice verification failed. Please try again.');
        setVerifying(false);
      }
    } catch (err) {
      console.error('Error during verification:', err);
      setError('An error occurred during verification');
      setVerifying(false);
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
              <p>🎤 Verifying your identity...</p>
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
    </div>
  );
}

export default LoginPage;
