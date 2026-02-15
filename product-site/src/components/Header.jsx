import { motion } from 'framer-motion'
import catphishLogo from '../assets/catphish_logo.png'
import Navbar from './Navbar'

function Header() {
  return (
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
  )
}

export default Header
