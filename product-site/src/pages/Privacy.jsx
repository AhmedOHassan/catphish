import { motion } from 'framer-motion'
import Header from '../components/Header'
import voiceDataProtectionImg from '../assets/voice_data_protection.png'
import secureProcessingImg from '../assets/secure_processing.png'
import completeOwnershipImg from '../assets/complete_ownership.png'

const privacyCards = [
  {
    title: 'Voice Data Protection',
    description: 'Your voiceprint is encrypted and stored securely. We never share raw audio data with third parties or use it for purposes beyond authentication.',
    image: voiceDataProtectionImg,
  },
  {
    title: 'Secure Processing',
    description: 'All voice analysis happens with end-to-end encryption. Your biometric data is protected with industry-leading security standards.',
    image: secureProcessingImg,
  },
  {
    title: 'Complete Ownership',
    description: 'Access, export, or delete your voice data anytime. You maintain complete ownership and control over your biometric information.',
    image: completeOwnershipImg,
  },
]

function Privacy() {
  return (
    <div className="page">
      <Header />
      <main className="page-content privacy-page">
        <motion.div
          className="privacy-container"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
        >
          {/* Header Section */}
          <div className="privacy-header">
            <h1 className="privacy-main-title">
              Your Voice Data, Protected and Secure
            </h1>
            <p className="privacy-main-description">
              Catphish prioritizes your privacy with transparent data practices, robust encryption, and complete user control over biometric information.
            </p>
          </div>

          {/* Feature Cards */}
          <div className="privacy-cards">
            {privacyCards.map((card, index) => (
              <motion.div
                key={card.title}
                className="privacy-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
              >
                <h3 className="privacy-card-title">{card.title}</h3>
                <p className="privacy-card-description">{card.description}</p>
                <div className="privacy-card-image">
                  {card.image ? (
                    <img src={card.image} alt={card.title} className="privacy-card-img" />
                  ) : (
                    <div className="privacy-card-gradient" />
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  )
}

export default Privacy
