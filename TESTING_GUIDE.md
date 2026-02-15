# Catphish Popup Integration - Testing Guide

## Overview
This implementation integrates the Catphish voice verification popup directly into the demo-website, allowing users to complete enrollment and verification without leaving the page.

## What's Been Implemented

### Backend (api/main.py)
- ✅ Updated CORS to allow requests from `http://localhost:5173` and `http://127.0.0.1:5173`
- ✅ Existing endpoints work: `/v1/enroll`, `/v1/challenges`, `/v1/challenges/{id}/verify`

### Frontend Components

#### 1. CatphishPopup Component (`catphish-api/src/components/CatphishPopup.jsx`)
A complete voice verification modal with the following features:
- **Step 0**: Request microphone permission
- **Step 1**: Record enrollment audio (5 seconds)
- **Step 2**: Submit enrollment to backend
- **Step 3**: Create challenge and display phrase
- **Step 4**: Record challenge response
- **Step 5**: Submit verification
- **Step 6**: Display results (status, similarity, AI probability, confidence score, risk level)

#### 2. Audio Recording Service (`catphish-api/src/services/audioRecorder.js`)
Handles all microphone recording functionality:
- Requests microphone permission via MediaRecorder API
- Records audio in WebM format
- Converts to WAV format (16kHz, 16-bit PCM)
- Converts WAV to base64 for API transmission

#### 3. API Client Service (`catphish-api/src/services/catphishClient.js`)
Direct integration with backend endpoints:
- `enroll()` - POST /v1/enroll with base64 audio
- `createChallenge()` - POST /v1/challenges
- `verify()` - POST /v1/challenges/{id}/verify
- All requests include `X-Catphish-Key` header

### Integration

#### demo-website LoginPage
- Integrated CatphishPopup component
- Popup opens after successful username/password login
- Passes user ID and API configuration to popup
- On completion, redirects to dashboard

## Testing the Implementation

### Prerequisites
1. Valkey running: `docker compose up -d`
2. Demo data seeded: `./scripts/seed-valkey.sh`
3. Backend API running on port 8000
4. Demo-website running on port 5173

### Test Scenario 1: Complete Flow (Enrollment + Verification)

1. **Open demo-website**
   - Navigate to `http://localhost:5173`
   
2. **Sign Up**
   - Click "Sign Up"
   - Enter email and password
   - Click "Sign Up" button
   
3. **Login**
   - Enter the same credentials
   - Click "Login" button
   
4. **Voice Verification Popup Opens**
   - Popup should appear automatically
   
5. **Step 0: Allow Microphone**
   - Click "Allow Microphone"
   - Browser will request microphone permission
   - Grant permission
   
6. **Step 1: Record Enrollment**
   - Popup shows "Voice Enrollment"
   - Click "Start Recording (5s)"
   - Speak anything for 5 seconds
   - Recording indicator shows progress
   - After 5s, shows "Recording complete!"
   - Click "Next →"
   
7. **Step 2: Submit Enrollment**
   - Click "Submit Enrollment"
   - Backend processes the audio and creates voice embedding
   - Should show "Enrolling..." then automatically proceed
   
8. **Step 3: Create Challenge**
   - Click "Create Challenge"
   - Backend creates a challenge with a random phrase
   - Phrase is displayed (e.g., "Unique New York, blue alpaca seven")
   
9. **Step 4: Record Challenge Response**
   - Read the phrase aloud clearly
   - Click "Start Recording (5s)"
   - Speak the phrase
   - After recording, click "Next →"
   
10. **Step 5: Verify**
    - Click "Verify Now"
    - Backend runs verification pipeline:
      - Layer 1: Speaker verification (embedding comparison)
      - Layer 2: AI detection
      - Layer 3: Comprehension check (phrase matching)
    
11. **Step 6: View Results**
    - Popup shows verification result:
      - ✅ Status: "verified" or ❌ "failed"
      - Confidence Score: percentage
      - Similarity: speaker matching score
      - AI Probability: likelihood of synthetic voice
      - Risk Level: low/medium/high
      - Reasons: detailed explanation
    - Click "Close" to dismiss popup
    
12. **Dashboard**
    - Should redirect to dashboard after successful verification

### Test Scenario 2: Error Handling

#### Test Microphone Denied
1. Login to demo-website
2. When popup opens, click "Allow Microphone"
3. Deny microphone permission in browser
4. Should show error: "Microphone access denied"

#### Test Backend Offline
1. Stop the backend API: `pkill -f uvicorn`
2. Login to demo-website
3. Popup opens but API calls will fail
4. Should show error messages for failed requests

#### Test Invalid Audio
1. Complete enrollment with normal audio
2. During verification, record silence or very short audio
3. Verification may fail with low confidence score

### Expected Results

#### Successful Verification Response:
```json
{
  "challenge_id": "ch_abc123",
  "external_user_id": "user_001",
  "status": "verified",
  "confidence_score": 0.85,
  "risk_level": "low",
  "reasons": ["all_layers_passed"],
  "similarity": 0.92,
  "ai_probability": 0.15
}
```

#### Failed Verification Response:
```json
{
  "challenge_id": "ch_abc123",
  "external_user_id": "user_001",
  "status": "failed",
  "confidence_score": 0.45,
  "risk_level": "high",
  "reasons": [
    "speaker_mismatch (similarity: 0.42)",
    "ai_detected (probability: 0.78)"
  ],
  "similarity": 0.42,
  "ai_probability": 0.78
}
```

## Verification Flow Details

### Enrollment (POST /v1/enroll)
- Receives base64-encoded WAV audio
- Creates voice embedding using Resemblyzer
- Stores embedding in Valkey with user ID
- Returns enrollment confirmation

### Challenge Creation (POST /v1/challenges)
- Generates random phrase (e.g., "Toy boat, toy boat, toy boat, sixteen")
- Creates challenge with TTL (120 seconds)
- Stores in Valkey
- Returns challenge ID and phrase

### Verification (POST /v1/challenges/{id}/verify)
1. **Rate Limiting**: Checks rate limits (5 requests/minute)
2. **Replay Protection**: Uses challenge lock mechanism
3. **Challenge Validation**: Ensures challenge exists and hasn't expired
4. **Layer 1 - Embedding**: Creates embedding from verification audio
5. **Layer 2 - Speaker Verification**: Compares with enrolled embedding
6. **Layer 3 - AI Detection**: Detects synthetic/cloned voices
7. **Layer 4 - Comprehension**: Verifies user said the correct phrase
8. **Final Decision**: Combines all layers for pass/fail verdict

## Known Limitations

1. **Audio Format**: Records in WebM, converts to WAV. Some browsers may have quality differences.
2. **Local Only**: Hardcoded to use `http://127.0.0.1:8000` (localhost)
3. **No Persistence**: User must complete entire flow in one session
4. **Single Enrollment**: Each login requires enrollment + verification (no persistent enrollment check)

## Troubleshooting

### Popup Doesn't Open
- Check browser console for errors
- Verify demo-website is running on port 5173
- Verify CatphishPopup component is imported correctly

### Microphone Not Working
- Check browser permissions (chrome://settings/content/microphone)
- Try different browser (Chrome/Firefox recommended)
- Verify MediaRecorder API is supported

### API Errors
- Check backend is running: `curl http://127.0.0.1:8000/health`
- Check CORS headers in browser Network tab
- Verify API key is correct: `demo_key_123`
- Check backend logs: `tail -f /tmp/copilot-detached-*.log`

### Valkey Connection Issues
- Verify Valkey is running: `docker ps | grep valkey`
- Test connection: `docker exec -it catphish-valkey valkey-cli PING`
- Check seeded data: `docker exec -it catphish-valkey valkey-cli HGETALL tenant:by_api_key:demo_key_123`

## Development Notes

### File Structure
```
catphish/
├── api/
│   └── main.py                    # Updated CORS configuration
├── catphish-api/
│   └── src/
│       ├── components/
│       │   └── CatphishPopup.jsx  # Main popup component
│       ├── services/
│       │   ├── catphishClient.js  # API client
│       │   └── audioRecorder.js   # Audio recording utilities
│       └── index.js               # Export for reuse
└── demo-website/
    └── src/
        └── pages/
            └── LoginPage.jsx      # Integrated popup
```

### Key Technologies
- React 18 (functional components with hooks)
- MediaRecorder API (audio recording)
- Web Audio API (WAV conversion)
- Vite (dev server and bundler)
- FastAPI (backend)
- Valkey (data store)

## Next Steps

For production deployment, consider:
1. Add persistent enrollment check (check if user already enrolled)
2. Support for enrollment-only or verification-only modes
3. Better error recovery and retry mechanisms
4. Audio quality validation before submission
5. Support for multiple audio formats
6. Configurable recording duration
7. Better visual feedback during processing
8. Accessibility improvements (keyboard navigation, screen readers)
