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
