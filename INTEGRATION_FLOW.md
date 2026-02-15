# Catphish Voice Verification - Integration Documentation

## Overview

The demo-website now integrates with the catphish-api frontend for voice verification. When users log in, they are redirected to the voice verification app to complete enrollment or verification.

## How It Works

### Flow Diagram

```
1. User logs in to demo-website (localhost:5173)
   ↓
2. Login successful → Redirects to catphish-api (localhost:3001)
   ↓
3. User completes voice verification on catphish-api
   ↓
4. Catphish-api redirects back to demo-website/dashboard
   ↓
5. Dashboard shows verification result
```

## Running Both Apps

### Terminal 1 - Demo Website (Banking App)
```bash
cd demo-website
npm install
npm run dev
```
Runs on: http://localhost:5173

### Terminal 2 - Catphish API (Voice Verification)
```bash
cd catphish-api
npm install
npm run dev
```
Runs on: http://localhost:3001

## Integration Details

### demo-website/src/services/catphishService.js

**Functions:**

1. `redirectToVoiceVerification(external_user_id, return_url)`
   - Stores user ID in localStorage
   - Redirects to catphish-api verification page
   - Saves return URL for after verification

2. `getVerificationResult()`
   - Checks URL params for verification status
   - Returns verification result from redirect

3. `returnFromVerification(success, session_id)`
   - Used by catphish-api to redirect back
   - Includes verification status in URL

### catphish-api Pages

**SuccessPage.jsx:**
- Auto-redirects back to demo-website after 2 seconds
- Includes `verification_status=success` in URL
- Passes session_id

**FailurePage.jsx:**
- Offers retry or return to app
- Includes `verification_status=failure` in URL

## Testing the Integration

### Step 1: Start Both Apps
```bash
# Terminal 1
cd demo-website && npm run dev

# Terminal 2
cd catphish-api && npm run dev
```

### Step 2: Sign Up on Demo Website
1. Go to http://localhost:5173
2. Click "Sign Up"
3. Create an account

### Step 3: Login (triggers voice verification)
1. Click "Login"
2. Enter credentials
3. You'll be redirected to http://localhost:3001/verify
4. Complete voice verification (simulated)
5. Get redirected back to http://localhost:5173/dashboard
6. See verification success message

## URL Parameters

### Redirect to Catphish-API
```
http://localhost:3001/verify
```
- User ID stored in localStorage as `external_user_id`
- Return URL stored as `catphish_return_url`

### Redirect Back to Demo Website

**Success:**
```
http://localhost:5173/dashboard?verification_status=success&session_id=session_xxx
```

**Failure:**
```
http://localhost:5173/dashboard?verification_status=failure&session_id=failed_xxx
```

## LocalStorage Keys

- `external_user_id` - User's ID for verification
- `catphish_return_url` - URL to return to after verification
- `enrolled_users` - Array of enrolled user IDs (demo only)

## Customization

### Change Catphish-API URL

In `demo-website/src/services/catphishService.js`:
```javascript
const CATPHISH_FRONTEND_URL = 'http://localhost:3001';
// Change to your catphish-api URL
```

### Change Return URL

In LoginPage or anywhere calling verification:
```javascript
redirectToVoiceVerification(userId, 'http://localhost:5173/custom-page');
```

## Production Considerations

1. **HTTPS**: Use HTTPS for both apps in production
2. **CORS**: Configure CORS if needed
3. **Session Management**: Implement proper session tokens
4. **Security**: Don't expose user_id in localStorage
5. **Error Handling**: Add proper error pages and retry logic
6. **Analytics**: Track verification success/failure rates

## Troubleshooting

### Issue: Redirect not working
- Ensure both apps are running
- Check browser console for errors
- Verify URLs in catphishService.js

### Issue: Lost after redirect
- Check localStorage for `catphish_return_url`
- Verify URL parameters are being passed

### Issue: Verification status not showing
- Check Dashboard.jsx is calling `getVerificationResult()`
- Verify URL params include `verification_status`

## Next Steps

- [ ] Implement real backend API
- [ ] Add real microphone recording
- [ ] Implement proper authentication tokens
- [ ] Add session management
- [ ] Deploy both apps
- [ ] Configure production URLs
