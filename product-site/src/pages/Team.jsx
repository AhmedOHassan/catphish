import { motion } from 'framer-motion'
import Header from '../components/Header'
import tristanPfp from '../assets/tristan_pfp.png'
import ahmedPfp from '../assets/ahmed_pfp.png'
import rameezPfp from '../assets/rameez_pfp.png'
import nolanPfp from '../assets/nolan_pfp.png'

const teamMembers = [
  {
    name: 'Tristan Curtis',
    image: tristanPfp,
    linkedin: 'https://www.linkedin.com/in/tristan-curtis-baabba304/',
  },
  {
    name: 'Ahmed Hassan',
    image: ahmedPfp,
    linkedin: 'https://www.linkedin.com/in/ahmedohassan/',
  },
  {
    name: 'Rameez Malik',
    image: rameezPfp,
    linkedin: 'https://www.linkedin.com/in/rameez-malik-ncsu/',
  },
  {
    name: 'Nolan Witt',
    image: nolanPfp,
    linkedin: 'https://www.linkedin.com/in/nolan-witt/',
  },
]

function Team() {
  return (
    <div className="page">
      <Header />
      <main className="page-content">
        <motion.h1
          className="page-title team-title"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
        >
          <span className="title-light">Meet the</span> <span className="title-bold">team.</span>
        </motion.h1>

        <motion.div
          className="team-grid"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
        >
          {teamMembers.map((member, index) => (
            <motion.a
              key={member.name}
              href={member.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="team-member"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              <div className="team-member-image">
                <img src={member.image} alt={member.name} />
                <div className="linkedin-badge">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </div>
              </div>
              <span className="team-member-name">{member.name}</span>
            </motion.a>
          ))}
        </motion.div>
      </main>
    </div>
  )
}

export default Team
