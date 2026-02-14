import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <Navbar 
        onLoginClick={() => navigate('/login')}
        onSignUpClick={() => navigate('/signup')}
      />
      <Hero />
    </div>
  );
}

export default LandingPage;
