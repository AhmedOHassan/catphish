# Catphish Voice Verification - React Frontend

A standalone React frontend for the Catphish voice verification system with simulated enrollment and verification flows.

## 🎯 Project Overview

This is a **demo-ready** React application that showcases voice biometric verification flows:
- **Flow A**: First-time enrollment for new users
- **Flow B**: Verification for returning users
- **Flow C**: Failure handling and retry logic

## ⚠️ Important

This is currently a **PLACEHOLDER IMPLEMENTATION** for demo purposes:
- ✅ Simulated audio recording (no real microphone access)
- ✅ localStorage for enrollment tracking
- ✅ Mock API responses with configurable success rate
- ⏳ Real backend integration (to be implemented)

## 📁 Project Structure

```
catphish-api/
├── src/
│   ├── App.jsx                          # Main app with routing
│   ├── main.jsx                         # Entry point
│   ├── index.css                        # Global styles
│   ├── pages/
│   │   ├── VerificationPage.jsx         # Voice enrollment/verification
│   │   ├── SuccessPage.jsx              # Successful verification
│   │   └── FailurePage.jsx              # Failed verification
│   └── services/
│       └── catphishService.js           # Voice verification API
├── .env                                 # Environment variables
├── package.json                         # Dependencies
├── vite.config.js                       # Vite configuration
└── index.html                           # HTML template
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables:
   - The `.env` file is already created with placeholder values
   - Update `VITE_CATPHISH_API_URL` and `VITE_CATPHISH_API_KEY` when ready for real API

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3001](http://localhost:3001) in your browser

### Build for Production

```bash
npm run build
```

The build output will be in the `dist/` folder.

## 🎬 User Flows

### Flow A: First-Time Enrollment

1. User visits `/` or `/verify` (new user, no stored voice)
2. System detects user is not enrolled
3. Displays message: **"To protect your account, please record your voice"**
4. Shows phrase: **"Silver tiger 42 jumps quickly"**
5. User clicks **"Start Recording"** (simulates 3-second recording)
6. User clicks **"Submit Enrollment"**
7. Calls `createVerificationSession(external_user_id, true)`
8. **Success (200)** → Redirects to `/success`
9. **Failure (401)** → Redirects to `/failure`

### Flow B: Returning User Verification

1. User visits `/verify` (enrolled user)
2. System detects user is enrolled
3. Displays message: **"User already enrolled. Please verify your identity"**
4. Shows dynamic phrase: e.g., **"Purple rocket 71 dances loudly"**
5. User records and submits
6. Calls `createVerificationSession(external_user_id, false)`
7. Redirects based on response status

### Flow C: Failure/Attacker

1. Simulated 401 response (20% chance in demo)
2. Redirects to `/failure` page
3. Shows failure details and possible reasons
4. Options to retry or contact support
5. Security warning about repeated attempts

## 📋 API Service

### Functions in `catphishService.js`

#### `checkUserEnrollment(external_user_id)`
Checks if a user has enrolled their voice biometric.

**Returns:**
```javascript
{
  enrolled: boolean,
  phrase: string
}
```

**TODO**: Replace with real API call to check enrollment status

---

#### `createVerificationSession(external_user_id, isEnrollment)`
Creates a verification or enrollment session.

**Parameters:**
- `external_user_id`: User's ID from your system
- `isEnrollment`: `true` for enrollment, `false` for verification

**Returns:**
```javascript
{
  status: number,        // 200 for success, 401 for failure
  session_id: string,
  message: string
}
```

**TODO**: Replace with real API call and include audio data

---

#### `generateVerificationPhrase()`
Generates a random phrase for voice verification.

**Returns:** Random phrase string (e.g., "Purple rocket 71 dances loudly")

## 🔐 Environment Variables

Create or modify `.env` file:

```env
VITE_CATPHISH_API_URL=https://api.catphish.com/verify
VITE_CATPHISH_API_KEY=your_api_key_here
```

Access in code using `import.meta.env.VITE_CATPHISH_API_URL`

## 🧪 Testing the Demo

### Scenario 1: First-Time User
1. Clear localStorage: `localStorage.clear()`
2. Visit `http://localhost:3001`
3. Should see enrollment flow
4. Complete enrollment
5. User is added to localStorage

### Scenario 2: Returning User
1. Visit `http://localhost:3001` again
2. Should see verification flow with dynamic phrase
3. Complete verification

### Scenario 3: Simulated Failure
- The demo has a 20% chance of returning 401 (failure)
- Retry until you see the failure page
- Test the retry and support buttons

### Reset Demo
Clear localStorage to reset:
```javascript
localStorage.clear()
```

## 🔧 Backend Integration

### Step 1: Update Environment Variables
Set real API URL and API key in `.env`

### Step 2: Implement Real Audio Recording
In `VerificationPage.jsx`, replace the `handleRecord` function with real microphone capture. See TODO comments in the code.

### Step 3: Update catphishService.js
Replace placeholder implementations with real API calls. Detailed instructions are in the TODO comments.

### Step 4: Backend Requirements
Your Python backend should implement these endpoints:

- **POST /enrollment/status** - Check enrollment
- **POST /enroll** - Enroll new user
- **POST /verify** - Verify returning user

See code comments for expected request/response formats.

## 📦 Dependencies

- **react** (^18.2.0) - UI framework
- **react-dom** (^18.2.0) - React DOM rendering
- **react-router-dom** (^6.20.0) - Client-side routing
- **vite** (^5.0.0) - Build tool and dev server

## 🎨 Features

✅ Simulated 3-second voice recording  
✅ Dynamic phrase generation  
✅ Enrollment detection via localStorage  
✅ Success/failure page routing  
✅ Clean, responsive UI  
✅ Loading states and visual feedback  
✅ Comprehensive TODO comments for real implementation  
✅ Error handling and user feedback  

## 📝 Next Steps

- [ ] Implement real microphone audio capture
- [ ] Connect to actual Catphish backend API
- [ ] Add proper authentication/session management
- [ ] Implement audio file upload
- [ ] Add error retry logic
- [ ] Implement rate limiting UI feedback
- [ ] Add accessibility features
- [ ] Cross-browser testing

## 🐛 Debugging

1. Check browser console for logs
2. Inspect localStorage for `external_user_id` and `enrolled_users`
3. Monitor Network tab for API calls (when real backend is connected)
4. Use React DevTools for component state inspection

## 📞 Support

For Catphish API documentation and support:
- Documentation: https://docs.catphish.com (placeholder)
- Support: support@catphish.com (placeholder)

## 📄 License

This is a demo project. Check with your organization for licensing.

---

**Note**: All TODO comments in the code indicate where real backend integration should happen. The current implementation is fully functional for demo purposes but uses simulated data and API responses.
