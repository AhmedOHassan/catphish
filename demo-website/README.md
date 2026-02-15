# SecureBank Demo Website

A simple demo banking website for demonstrating Catphish voice verification API integration.

## ⚠️ Important

This demo website integrates with the Catphish API backend. To use voice verification:

**Requirements:**
- Catphish API backend running on port 8000
- Catphish-api frontend running on port 3001
- Valkey database running via Docker

See the main [README.md](../README.md) for complete setup instructions.

## Features

- 🔐 User Sign Up & Login
- 💳 Fake Banking Dashboard
- 🎤 Real Catphish Voice Verification API Integration (session-based URLs)
- 📱 Responsive Design

## Getting Started

### Quick Start (Frontend Only)
If you just want to see the UI without voice verification:

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

**Note:** Voice verification will fail if backend is not running. You'll see an error message with instructions.

### Full Setup (With Voice Verification)
See the main [README.md](../README.md) for instructions on running all services.

## How It Works
  
1. **Sign Up**: Creates a new user and stores it in localStorage
2. **Login**: Validates credentials against localStorage
3. **API Call**: Calls `/v1/verification-sessions` to create a session
4. **Redirect**: Redirects to catphish-api with session_id (not user_id)
5. **Verification**: User completes voice verification
6. **Dashboard**: Shows fake banking data if verification succeeds

## Architecture

```
demo-website (port 3000)
    ↓ POST /v1/verification-sessions
Catphish API (port 8000)
    ↓ Returns session_id
demo-website redirects to
    ↓
catphish-api (port 3001) with ?session_id=vs_xxx
```
