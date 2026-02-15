import { motion } from 'framer-motion'
import Header from '../components/Header'

function Documentation() {
  return (
    <div className="page">
      <Header />
      <main className="page-content">
        <motion.h1
          className="page-title"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
        >
          Documentation
        </motion.h1>
      </main>
    </div>
  )
}

export default Documentation
