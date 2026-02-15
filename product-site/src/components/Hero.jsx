import { motion } from 'framer-motion'
import catphishLogo from '../assets/catphish_logo.png'
import Navbar from './Navbar'

function Hero() {
  return (
    <section className="hero">
      {/* Header with Logo and Navbar */}
      <motion.header
        className="header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <div className="logo-container">
          <img src={catphishLogo} alt="Catphish Logo" className="logo-image" />
          <span className="logo-text">Catphish</span>
        </div>
        <Navbar />
        <div className="header-spacer" />
      </motion.header>

      {/* Hero Content */}
      <div className="hero-content">
        {/* Tagline */}
      <motion.h1
        className="hero-tagline"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.3 }}
      >
        Next-Gen Voice Security
        <br />
        <span className="tagline-highlight">for Modern Systems</span>
      </motion.h1>

      {/* Description */}
      <motion.p
        className="hero-description"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.5 }}
      >
        AI-powered voice biometrics and liveness detection to stop cloning attacks
        and social engineering at the login flow.
      </motion.p>

      {/* Optional CTA Button */}
      <motion.div
        className="hero-cta"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.7 }}
      >
        <button className="cta-button">Get Started</button>
      </motion.div>
      </div>
    </section>
  )
}

export default Hero
