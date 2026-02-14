import React from 'react';

function Hero() {
  return (
    <div className="hero">
      <div className="hero-container">
        <div className="hero-content">
          <h1 className="hero-title">
            Banking Made <span className="highlight">Secure</span>
          </h1>
          <p className="hero-subtitle">
            Experience next-generation banking with voice-verified security. 
            Your money, protected by cutting-edge biometric authentication.
          </p>
          
          <div className="hero-features">
            <div className="feature">
              <span className="feature-icon">🎤</span>
              <div className="feature-text">
                <h3>Voice Authentication</h3>
                <p>Secure login with voice verification</p>
              </div>
            </div>
            <div className="feature">
              <span className="feature-icon">🔐</span>
              <div className="feature-text">
                <h3>Bank-Grade Security</h3>
                <p>Military-grade encryption</p>
              </div>
            </div>
            <div className="feature">
              <span className="feature-icon">⚡</span>
              <div className="feature-text">
                <h3>Instant Transfers</h3>
                <p>Send money in seconds</p>
              </div>
            </div>
          </div>
        </div>

        <div className="hero-image">
          <div className="hero-card">
            <div className="card-chip"></div>
            <div className="card-number">•••• •••• •••• 4242</div>
            <div className="card-holder">SECURE BANK</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Hero;
