import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'

const tabs = [
  { id: 'product', label: 'Product', path: '/' },
  { id: 'documentation', label: 'API Documentation', path: '/documentation' },
  { id: 'team', label: 'Team', path: '/team' },
  { id: 'privacy', label: 'Privacy Policy', path: '/privacy' },
]

function Navbar() {
  const location = useLocation()

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <nav className="navbar">
      {tabs.map((tab) => (
        <NavLink
          key={tab.id}
          to={tab.path}
          className={`navbar-tab ${isActive(tab.path) ? 'active' : ''}`}
        >
          {isActive(tab.path) && (
            <motion.div
              className="navbar-tab-bg"
              layoutId="activeTab"
              initial={false}
              transition={{ type: 'spring', stiffness: 500, damping: 35 }}
            />
          )}
          <span className="navbar-tab-label">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  )
}

export default Navbar
