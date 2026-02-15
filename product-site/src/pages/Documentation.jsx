import { motion } from 'framer-motion';
import Header from '../components/Header';

export default function Documentation() {
  return (
    <div className="page api-docs-page">
      <Header />
      <main className="api-docs-content">
        {/* Header */}
        <motion.div 
          className="api-docs-header"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h1 className="api-docs-title">Catphish API Documentation</h1>
          <p className="api-docs-subtitle">Voice verification as a service • No domain required</p>
        </motion.div>

        {/* Quick Start */}
        <motion.div 
          className="api-quick-start"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h3 className="api-quick-title">Quick Start (curl)</h3>
          <code className="api-curl">curl -X POST http://104.238.165.56:8000/v1/enroll -H "X-Catphish-Key: demo_key_123" -d '&#123;"external_user_id":"user_123","audio_sample":"..."&#125;'</code>
        </motion.div>

        {/* Horizontal Cards Row */}
        <motion.div 
          className="api-cards-horizontal"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          {/* Connection */}
          <div className="api-card api-card-compact">
            <h2 className="api-card-title">Connection</h2>
            <div className="api-card-content">
              <div className="api-field">
                <p className="api-label">Base URL</p>
                <code className="api-code">http://104.238.165.56:8000</code>
              </div>
              <div className="api-field">
                <p className="api-label">Authentication Header</p>
                <code className="api-code">X-Catphish-Key: demo_key_123</code>
              </div>
            </div>
          </div>

          {/* Enroll */}
          <div className="api-card api-card-compact">
            <h3 className="api-example-title">POST /v1/enroll</h3>
            <pre className="api-pre">{`{
  "external_user_id": "user_123",
  "audio_sample": "base64_audio_data",
  "metadata": {"reason": "initial"}
}`}</pre>
          </div>

          {/* Create Challenge */}
          <div className="api-card api-card-compact">
            <h3 className="api-example-title">POST /v1/challenges</h3>
            <pre className="api-pre">{`{
  "external_user_id": "user_123",
  "purpose": "login",
  "ttl_seconds": 120
}`}</pre>
            <p className="api-note">→ Returns challenge_id & phrase</p>
          </div>

          {/* Verify Challenge */}
          <div className="api-card api-card-compact">
            <h3 className="api-example-title">POST /v1/challenges/:id/verify</h3>
            <pre className="api-pre">{`{
  "external_user_id": "user_123",
  "audio_sample": "base64_audio_data"
}`}</pre>
            <p className="api-note">→ Returns: verified | failed | expired</p>
          </div>
        </motion.div>

        {/* Two Column Layout */}
        <motion.div 
          className="api-docs-grid"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          
          {/* Left Column - Endpoints */}
          <div className="api-docs-column">
            <div className="api-card">
              <h2 className="api-card-title">Endpoints</h2>
              <div className="api-endpoints">
                <div className="api-endpoint">
                  <span className="api-method api-method-get">GET</span>
                  <code className="api-path">/health</code>
                </div>
                <div className="api-endpoint">
                  <span className="api-method api-method-post">POST</span>
                  <code className="api-path">/v1/enroll</code>
                </div>
                <div className="api-endpoint">
                  <span className="api-method api-method-post">POST</span>
                  <code className="api-path">/v1/challenges</code>
                </div>
                <div className="api-endpoint">
                  <span className="api-method api-method-post">POST</span>
                  <code className="api-path">/v1/challenges/:id/verify</code>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Status Codes */}
          <div className="api-docs-column">
            <div className="api-card">
              <h2 className="api-card-title">Status Codes</h2>
              <div className="api-status-grid">
                <div className="api-status"><code className="status-success">200</code> Success</div>
                <div className="api-status"><code className="status-success">201</code> Created</div>
                <div className="api-status"><code className="status-error">400</code> Bad Request</div>
                <div className="api-status"><code className="status-error">401</code> Unauthorized</div>
                <div className="api-status"><code className="status-error">404</code> Not Found</div>
                <div className="api-status"><code className="status-error">409</code> Conflict</div>
              </div>
            </div>
          </div>

        </motion.div>
      </main>
    </div>
  );
}
