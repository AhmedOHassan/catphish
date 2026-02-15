# SecureBank Demo Website

A simple demo banking website for demonstrating Catphish voice verification API integration.

## ⚠️ Important

This is a **DEMO ONLY** website. It uses:
- **localStorage** for user storage (no database)
- **No backend server**
- **Placeholder API calls** (not real Catphish implementation)

## Features

- 🔐 User Sign Up & Login
- 💳 Fake Banking Dashboard
- 🎤 Placeholder Catphish Voice Verification API Integration
- 📱 Responsive Design

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

## How It Works
  
1. **Sign Up**: Creates a new user and stores it in localStorage
2. **Login**: Validates credentials against localStorage
3. **API Call**: Makes a placeholder call to `catphishService.js`
4. **Dashboard**: Shows fake banking data if verification succeeds

## Integrating Real Catphish API

To integrate the real Catphish API, replace the placeholder function in:
```
src/services/catphishService.js
```

Replace the mock implementation with actual API calls to your Catphish endpoint.
