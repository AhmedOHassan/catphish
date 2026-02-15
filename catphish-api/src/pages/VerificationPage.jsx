import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

import { getSessionStatus, enrollVoice, verifyVoice } from "../services/catphishService";
import useAudioRecorder from "../hooks/useAudioRecorder";

import "./VerificationPage.css";

export default function VerificationPage() {
  const navigate = useNavigate();

  // Session state
  const [loading, setLoading] = useState(true);
  const [sessionId, setSessionId] = useState("");
  const [externalUserId, setExternalUserId] = useState("");
  const [returnUrl, setReturnUrl] = useState("");
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [phrase, setPhrase] = useState("");
  const [phraseType, setPhraseType] = useState(""); // 'enrollment' | 'verification'
  const [errorMsg, setErrorMsg] = useState("");

  // Processing state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  // Audio recorder hook
  const {
    isRecording,
    audioBase64,
    error: micError,
    recordingTime,
    startRecording,
    stopRecording,
    reset: resetAudio,
  } = useAudioRecorder();

  const formatTime = (s) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  const title = isEnrolled ? "Voice Verification" : "Voice Enrollment";
  const subtitle = isEnrolled
    ? "Welcome back. Follow the instruction carefully, then record."
    : "Set up voice protection by following each instruction, then record.";

  const loadSession = async (sid) => {
    try {
      setLoading(true);
      const data = await getSessionStatus(sid);

      setExternalUserId(data.external_user_id);
      setReturnUrl(data.return_url || "");
      setIsEnrolled(Boolean(data.enrolled));
      setPhrase(data.phrase || "");
      setPhraseType(data.phrase_type || (data.enrolled ? "verification" : "enrollment"));

      // Store return_url so Success/Failure pages can use it
      if (data.return_url) {
        localStorage.setItem("catphish_return_url", data.return_url);
      }
    } catch (err) {
      console.error("Session load error:", err);
      setErrorMsg("Failed to load verification session. It may have expired.");
    } finally {
      setLoading(false);
    }
  };

  // On mount: read session_id from URL, fetch session status
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sid = params.get("session_id");

    if (!sid) {
      setErrorMsg("Invalid verification link — missing session_id.");
      setLoading(false);
      return;
    }

    setSessionId(sid);
    loadSession(sid);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const enrollmentLines = useMemo(() => {
    if (!phrase) return [];
    return phrase.split("\n").map((l) => l.trim()).filter(Boolean);
  }, [phrase]);

  // Submit audio to backend
  const handleSubmit = async () => {
    if (!audioBase64) return;

    setIsSubmitting(true);
    setStatusMessage(isEnrolled ? "Verifying your voice..." : "Enrolling your voice...");

    try {
      if (isEnrolled) {
        // Returning user → verify
        const result = await verifyVoice(sessionId, audioBase64);
        if (result.status === "verified") {
          navigate("/success", { state: { result } });
        } else {
          navigate("/failure", { state: { result, sessionId } });
        }
      } else {
        // New user → enroll
        const result = await enrollVoice(sessionId, audioBase64);
        if (result.success) {
          navigate("/success", { state: { result, enrollment: true } });
        } else {
          navigate("/failure", { state: { result, sessionId } });
        }
      }
    } catch (err) {
      console.error("Submit error:", err);
      navigate("/failure", { state: { error: err?.message || "Unknown error" } });
    } finally {
      setIsSubmitting(false);
      setStatusMessage("");
    }
  };

  const handleReRecord = () => {
    resetAudio();
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 14, filter: "blur(6px)" },
    show: {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      transition: { duration: 0.35, ease: "easeOut", staggerChildren: 0.06 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } },
  };

  // Error state
  if (errorMsg) {
    return (
      <div className="vp-page">
        <motion.div className="vp-card" variants={cardVariants} initial="hidden" animate="show">
          <motion.div className="vp-errorIcon" variants={itemVariants}>
            !
          </motion.div>
          <motion.h1 className="vp-title vp-titleError" variants={itemVariants}>
            Session Error
          </motion.h1>
          <motion.p className="vp-subtitle" variants={itemVariants}>
            {errorMsg}
          </motion.p>
        </motion.div>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="vp-page">
        <motion.div className="vp-card" variants={cardVariants} initial="hidden" animate="show">
          <motion.div className="vp-spinner" variants={itemVariants} />
          <motion.p className="vp-loadingText" variants={itemVariants}>
            Loading verification session…
          </motion.p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="vp-page">
      <motion.div className="vp-card" variants={cardVariants} initial="hidden" animate="show">
        {/* Header */}
        <motion.div variants={itemVariants}>
          <div className="vp-kicker">{isEnrolled ? "🔐 Verification" : "🎤 Enrollment"}</div>
          <h1 className="vp-title">{title}</h1>
          <p className="vp-subtitle">{subtitle}</p>
        </motion.div>

        {/* Instruction */}
        <motion.div className="vp-panel" variants={itemVariants}>
          {phraseType === "verification" ? (
            <>
              <div className="vp-panelLabel">Follow this instruction</div>
              <div className="vp-instruction">{phrase}</div>
              <div className="vp-hint">⚡ Don’t just read it — follow the instruction.</div>
            </>
          ) : (
            <>
              <div className="vp-panelLabel">Follow each instruction in order</div>
              <div className="vp-enrollmentList">
                {enrollmentLines.map((line, i) => (
                  <div key={i} className="vp-enrollmentItem">
                    {line}
                  </div>
                ))}
              </div>
              <div className="vp-hint">⚡ Don’t just read them — follow each instruction.</div>
            </>
          )}
        </motion.div>

        {/* Microphone error */}
        <AnimatePresence>
          {micError && (
            <motion.div
              className="vp-alert"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              transition={{ duration: 0.2 }}
            >
              ⚠️ {micError}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Controls */}
        <motion.div className="vp-controls" variants={itemVariants}>
          {/* State 1: Not recorded yet, not recording */}
          {!audioBase64 && !isRecording && (
            <button className="vp-btn vp-btnPrimary" onClick={startRecording} disabled={isSubmitting}>
              🎤 Start Recording
            </button>
          )}

          {/* State 2: Recording in progress */}
          {isRecording && (
            <div className="vp-recordingWrap">
              <div className="vp-recordingRow">
                <span className="vp-dot" />
                <span className="vp-recordingText">Recording… {formatTime(recordingTime)}</span>
              </div>

              <button className="vp-btn vp-btnSecondary" onClick={stopRecording} disabled={isSubmitting}>
                ◼ Stop Recording
              </button>
            </div>
          )}

          {/* State 3: Recorded, ready to submit */}
          {audioBase64 && !isRecording && !isSubmitting && (
            <>
              <div className="vp-success">✓ Recording complete</div>

              <button className="vp-btn vp-btnPrimary" onClick={handleSubmit}>
                {isEnrolled ? "🔍 Verify Voice" : "✓ Submit Enrollment"}
              </button>

              <button className="vp-btn vp-btnGhost" onClick={handleReRecord}>
                🔄 Re-record
              </button>
            </>
          )}

          {/* State 4: Submitting */}
          {isSubmitting && (
            <div className="vp-submitting">
              <div className="vp-spinner" />
              <div className="vp-loadingText">{statusMessage}</div>
            </div>
          )}
        </motion.div>

        {/* Info footer (kept, but styled) */}
        <motion.div className="vp-footer" variants={itemVariants}>

        </motion.div>
      </motion.div>
    </div>
  );
}

