import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signUp } from '../services/authService';
import Navbar from '../components/Navbar';

function SignUpPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validate inputs
    if (!email || !password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    // Sign up user
    const result = signUp(email, password);
    
    setLoading(false);

    if (result.success) {
      // Redirect to login page
      navigate('/login', { state: { message: 'Account created! Please log in.' } });
    } else {
      setError(result.message);
    }
  };

  return (
    <div className="signup-page">
      <Navbar 
        onLoginClick={() => navigate('/login')}
        onSignUpClick={() => navigate('/signup')}
      />
      
      <div className="auth-container">
        <div className="auth-card">
          <h1>Create Account</h1>
          <p className="subtitle">Join SecureBank today</p>

          {error && <div className="error-message">{error}</div>}

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
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a password"
                required
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account?{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/login'); }}>
              Log in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default SignUpPage;
