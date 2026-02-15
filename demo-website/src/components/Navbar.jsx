import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Navbar({ isLoggedIn = false, userEmail = '', onLoginClick, onSignUpClick, onLogout }) {
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Logo */}
        <div className="nav-logo" onClick={handleLogoClick}>
          <span className="logo-icon">🔒</span>
          <span className="logo-text">SecureBank</span>
        </div>

        {/* Navigation Items */}
        <div className="nav-items">
          {!isLoggedIn ? (
            // Logged out state
            <>
              <button onClick={onLoginClick} className="btn-secondary">
                Login
              </button>
              <button onClick={onSignUpClick} className="btn-primary">
                Sign Up
              </button>
            </>
          ) : (
            // Logged in state
            <div className="user-menu">
              <button 
                className="user-email-btn"
                onClick={() => setShowDropdown(!showDropdown)}
              >
                {userEmail}
                <span className="dropdown-arrow">▼</span>
              </button>
              
              {showDropdown && (
                <div className="dropdown-menu">
                  <button onClick={onLogout} className="dropdown-item">
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
