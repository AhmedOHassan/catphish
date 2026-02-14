import { useState } from 'react'
import { motion } from 'framer-motion'

const tabs = [
  { id: 'product', label: 'Product' },
  { id: 'documentation', label: 'Documentation' },
  { id: 'team', label: 'Team' },
]

function Navbar() {
  const [activeTab, setActiveTab] = useState('product')

  return (
    <nav className="navbar">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={`navbar-tab ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => setActiveTab(tab.id)}
        >
          {activeTab === tab.id && (
            <motion.div
              className="navbar-tab-bg"
              layoutId="activeTab"
              initial={false}
              transition={{ type: 'spring', stiffness: 500, damping: 35 }}
            />
          )}
          <span className="navbar-tab-label">{tab.label}</span>
        </button>
      ))}
    </nav>
  )
}

export default Navbar
