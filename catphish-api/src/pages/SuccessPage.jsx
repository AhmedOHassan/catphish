import React from "react";
import { useLocation } from "react-router-dom";
import { motion } from "framer-motion";

export default function SuccessPage() {
  const location = useLocation();
  const result = location.state?.result || {};
  const isEnrollment = location.state?.enrollment || false;

  const handleReturnToApp = () => {
    const returnUrl =
      localStorage.getItem("catphish_return_url") ||
      "http://localhost:3000/dashboard";
    localStorage.removeItem("catphish_return_url");

    const url = new URL(returnUrl);
    url.searchParams.set("verification_status", "success");
    window.location.href = url.toString();
  };

  const hasReturnUrl = Boolean(localStorage.getItem("catphish_return_url"));

  return (
    <div className="cp-shell">
      <div className="cp-bgGlow" aria-hidden="true" />

      <motion.div
        className="cp-card"
        initial={{ opacity: 0, y: 14, scale: 0.99 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <motion.div
          className="cp-iconWrap"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.08, duration: 0.35, ease: "easeOut" }}
        >
          <div className="cp-icon" aria-hidden="true">
            ✓
          </div>
        </motion.div>

        <motion.h1
          className="cp-title"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.12, duration: 0.35, ease: "easeOut" }}
        >
          {isEnrollment ? "Voice Enrolled!" : "Voice Verified!"}
        </motion.h1>

        <motion.p
          className="cp-subtitle"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.16, duration: 0.35, ease: "easeOut" }}
        >
          {isEnrollment
            ? "Your voice has been enrolled successfully. Your account is now protected."
            : "Your voice has been successfully verified. Access granted."}
        </motion.p>

        <motion.div
          className="cp-actions"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.35, ease: "easeOut" }}
        >
          <button className="cp-btnPrimary" onClick={handleReturnToApp}>
            {hasReturnUrl ? "Continue to Application" : "Continue"}
          </button>
        </motion.div>

        <motion.div
          className="cp-info"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.24, duration: 0.35, ease: "easeOut" }}
        >
          <p className="cp-infoText">
            🔒 Your voice biometric has been securely verified using Catphish
            technology.
          </p>

          {result?.solana_tx?.explorer_url && (
            <p className="cp-infoText">
              ⛓️{" "}
              <a
                className="cp-link"
                href={result.solana_tx.explorer_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                View audit trail on Solana
              </a>
            </p>
          )}
        </motion.div>
      </motion.div>

      {/* Self-contained theme styles (matches the VerificationPage look) */}
      <style>{`
        .cp-shell{
          min-height:100vh;
          display:flex;
          align-items:center;
          justify-content:center;
          padding:24px;
          background: linear-gradient(to top, #2a2a2a 0%, #0a0a0a 100%);
          color:#fff;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
          position:relative;
          overflow:hidden;
        }

        .cp-bgGlow{
          position:absolute;
          inset:-120px;
          background:
            radial-gradient(900px 600px at 20% 20%, rgba(255,255,255,0.06), transparent 60%),
            radial-gradient(700px 520px at 80% 30%, rgba(255,255,255,0.04), transparent 62%),
            radial-gradient(800px 600px at 55% 85%, rgba(255,255,255,0.03), transparent 60%);
          filter: blur(2px);
          pointer-events:none;
        }

        .cp-card{
          width:min(680px, 100%);
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 18px;
          padding: 28px 26px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.55);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          position:relative;
        }

        .cp-iconWrap{
          display:flex;
          justify-content:center;
          margin-bottom: 14px;
        }

        .cp-icon{
          width: 84px;
          height: 84px;
          border-radius: 999px;
          display:flex;
          align-items:center;
          justify-content:center;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.12);
          box-shadow: 0 10px 30px rgba(0,0,0,0.35);
          font-size: 44px;
          line-height: 1;
          user-select:none;
        }

        .cp-title{
          margin: 0 0 10px 0;
          text-align:center;
          font-weight: 800;
          letter-spacing: -0.03em;
          font-size: clamp(28px, 4vw, 44px);
          background: linear-gradient(
            90deg,
            #f2f2f2 0%,
            #bdbdbd 25%,
            #ffffff 50%,
            #bdbdbd 75%,
            #f2f2f2 100%
          );
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
        }

        .cp-subtitle{
          margin: 0 0 18px 0;
          text-align:center;
          font-size: 16px;
          line-height: 1.55;
          color: rgba(255,255,255,0.72);
        }

        .cp-actions{
          display:flex;
          justify-content:center;
          margin: 10px 0 16px;
        }

        .cp-btnPrimary{
          appearance:none;
          border: none;
          cursor:pointer;
          background: #ffffff;
          color:#000;
          border-radius: 999px;
          padding: 1rem 2.5rem;
          font-weight: 800;
          font-size: 16px;
          box-shadow: 0 4px 15px rgba(0,0,0,0.3);
          transform: translateY(0);
          transition: transform 150ms ease, background 150ms ease, box-shadow 150ms ease;
        }

        .cp-btnPrimary:hover{
          transform: translateY(-2px);
          background: #e0e0e0;
          box-shadow: 0 10px 28px rgba(0,0,0,0.38);
        }

        .cp-btnPrimary:active{
          transform: translateY(0);
        }

        .cp-info{
          margin-top: 10px;
          padding: 14px 14px;
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 14px;
        }

        .cp-infoText{
          margin: 6px 0;
          color: rgba(255,255,255,0.72);
          font-size: 13.5px;
          line-height: 1.45;
        }

        .cp-link{
          color: rgba(255,255,255,0.92);
          text-decoration: underline;
          text-underline-offset: 3px;
        }

        .cp-link:hover{
          color: #ffffff;
        }
      `}</style>
    </div>
  );
}

