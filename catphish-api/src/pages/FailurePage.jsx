import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

export default function FailurePage() {
  const navigate = useNavigate();
  const location = useLocation();

  const result = location.state?.result || {};
  const errorMessage = location.state?.error || "";

  // Optional: backend may include reasons; if not, show common causes as guidance.
  const backendReasons = Array.isArray(result.reasons) ? result.reasons : [];
  const displayReasons = backendReasons.length
    ? backendReasons
    : [
        "Background noise interfered with the recording",
        "Your voice didn’t match the enrolled profile",
        "Low audio quality or microphone issues",
        "Incorrect phrase spoken",
      ];

  const message =
    result.message ||
    errorMessage ||
    "We couldn't verify your voice. This can happen for a few different reasons.";

  const handleRetry = () => {
    // Go back to verification page with the same session to retry.
    const sid = location.state?.sessionId;
    if (sid) {
      navigate(`/verify?session_id=${sid}`);
      return;
    }

    // No session available — redirect to parent app to start fresh.
    const returnUrl = localStorage.getItem("catphish_return_url");
    if (returnUrl) {
      localStorage.removeItem("catphish_return_url");
      window.location.href = returnUrl;
      return;
    }

    window.location.href = "http://localhost:3000/login";
  };

  const handleReturnToApp = () => {
    // Clean up.
    localStorage.removeItem("catphish_return_url");
    localStorage.removeItem("pending_login_user");

    // Go straight to login page.
    window.location.href = "http://localhost:3000/login";
  };

  // Keeping these for parity with your earlier implementation (even if unused by default).
  // eslint-disable-next-line no-unused-vars
  const handleGoHome = () => {
    const returnUrl = localStorage.getItem("catphish_return_url");
    if (returnUrl) {
      handleReturnToApp();
    } else {
      window.location.href = "/";
    }
  };

  // eslint-disable-next-line no-unused-vars
  const handleContactSupport = () => {
    alert("In production, this would open a support contact form or help center.");
  };

  return (
    <div className="cp-shell">
      <style>{css}</style>

      <motion.div
        className="cp-card"
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      >
        <div className="cp-iconWrap" aria-hidden="true">
          <div className="cp-icon cp-icon--fail">✕</div>
        </div>

        <h1 className="cp-title">Verification Failed</h1>
        <p className="cp-subtitle">{message}</p>

        <div className="cp-grid">
          <div className="cp-panel">
            <div className="cp-panelTitle">Details</div>

            <div className="cp-kv">
              <div className="cp-k">Status</div>
              <div className="cp-v">❌ {result.status || "failed"}</div>
            </div>

            <div className="cp-kv">
              <div className="cp-k">Timestamp</div>
              <div className="cp-v">{new Date().toLocaleString()}</div>
            </div>

            {result.similarity != null && (
              <div className="cp-kv">
                <div className="cp-k">Voice similarity</div>
                <div className="cp-v">{(result.similarity * 100).toFixed(1)}%</div>
              </div>
            )}
          </div>

          <div className="cp-panel">
            <div className="cp-panelTitle">Common causes</div>
            <ul className="cp-list">
              {displayReasons.map((r, idx) => (
                <li key={`${idx}-${r}`}>{r}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="cp-actions">
          <button type="button" className="cp-btn cp-btn--primary" onClick={handleRetry}>
            Try again
          </button>

          <button type="button" className="cp-btn cp-btn--ghost" onClick={handleReturnToApp}>
            Return to login
          </button>
        </div>

        <div className="cp-footnote">
          If this keeps failing, try a quieter room and speak clearly.
        </div>
      </motion.div>
    </div>
  );
}

const css = `
.cp-shell{
  min-height:100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  padding:24px;
  background: linear-gradient(to top, #2a2a2a 0%, #0a0a0a 100%);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  color:#fff;
}

.cp-card{
  width:min(820px, 100%);
  background: rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 28px 26px;
  box-shadow: 0 14px 50px rgba(0,0,0,0.45);
  backdrop-filter: blur(12px);
}

.cp-iconWrap{display:flex; justify-content:center; margin-bottom:14px;}
.cp-icon{
  width:92px; height:92px;
  display:flex; align-items:center; justify-content:center;
  border-radius: 999px;
  font-size: 44px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.02);
}
.cp-icon--fail{ box-shadow: 0 0 0 6px rgba(255,255,255,0.02) inset; }

.cp-title{
  margin: 6px 0 10px;
  text-align:center;
  font-size: clamp(28px, 4vw, 44px);
  letter-spacing: -0.03em;
  font-weight: 800;
  background: linear-gradient(90deg, #f2f2f2 0%, #cfcfcf 25%, #f7f7f7 55%, #bdbdbd 80%, #f2f2f2 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.cp-subtitle{
  margin: 0 auto 18px;
  max-width: 62ch;
  text-align:center;
  color: rgba(255,255,255,0.7);
  line-height: 1.55;
}

.cp-grid{
  display:grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin: 14px 0 18px;
}
@media (min-width: 780px){
  .cp-grid{grid-template-columns: 1fr 1fr;}
}

.cp-panel{
  background: rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 16px;
}
.cp-panel:hover{border-color: rgba(255,255,255,0.15);}

.cp-panelTitle{
  font-size: 13px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.55);
  margin-bottom: 10px;
}

.cp-kv{
  display:flex;
  justify-content:space-between;
  gap: 12px;
  padding: 8px 0;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.cp-kv:first-of-type{border-top: 0; padding-top: 0;}
.cp-k{color: rgba(255,255,255,0.62); font-weight: 600;}
.cp-v{color: rgba(255,255,255,0.92); font-weight: 600;}

.cp-list{margin: 0; padding-left: 18px; color: rgba(255,255,255,0.75); line-height: 1.6;}
.cp-list li{margin: 6px 0;}

.cp-actions{
  display:flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 10px;
}
@media (min-width: 520px){
  .cp-actions{flex-direction: row; justify-content:center;}
}

.cp-btn{
  border: 0;
  border-radius: 999px;
  padding: 14px 24px;
  font-weight: 800;
  cursor: pointer;
  transition: transform .15s ease, filter .15s ease, background-color .15s ease, border-color .15s ease;
}

.cp-btn:focus{outline: none; box-shadow: 0 0 0 3px rgba(255,255,255,0.15);}

.cp-btn--primary{
  background: #fff;
  color: #0a0a0a;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.cp-btn--primary:hover{transform: translateY(-2px); filter: brightness(0.95);}

.cp-btn--ghost{
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.9);
  border: 1px solid rgba(255,255,255,0.12);
}
.cp-btn--ghost:hover{transform: translateY(-2px); border-color: rgba(255,255,255,0.2);}

.cp-footnote{
  margin-top: 16px;
  text-align:center;
  font-size: 13px;
  color: rgba(255,255,255,0.5);
}
`;

