# Catphish API Integration Guide

This document explains how to integrate the real Catphish voice verification API into this demo website.

## Current Implementation (Placeholder)

The placeholder API is located in: `src/services/catphishService.js`

Currently, it returns a mock response after a 1-second delay:

```javascript
{
  status: 200,
  session_id: "demo_session_123"
}
```

## Integration Flow

### 1. When the user logs in:

```
LoginPage.jsx → login() → createVerificationSession(user.id)
```

### 2. The function sends:

```javascript
{
  external_user_id: "user_123" // The user's ID from localStorage
}
```

### 3. Expected Response:

- **Success (200)**: User is redirected to Dashboard
- **Failure (non-200)**: User stays on login page with error message

## How to Replace with Real API

Open `src/services/catphishService.js` and replace the function:

```javascript
export async function createVerificationSession(external_user_id) {
  try {
    const response = await fetch('YOUR_CATPHISH_API_ENDPOINT', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY' // Add if required
      },
      body: JSON.stringify({
        external_user_id: external_user_id
      })
    });

    const data = await response.json();

    return {
      status: response.status,
      session_id: data.session_id || null
    };
  } catch (error) {
    console.error('Catphish API Error:', error);
    return {
      status: 500,
      session_id: null
    };
  }
}
```

## Configuration

You may want to add environment variables for:

- API endpoint URL
- API key/token
- Other configuration

Create a `.env` file:

```
VITE_CATPHISH_API_URL=https://api.catphish.com/verify
VITE_CATPHISH_API_KEY=your_api_key_here
```

Then use in your code:

```javascript
const API_URL = import.meta.env.VITE_CATPHISH_API_URL;
const API_KEY = import.meta.env.VITE_CATPHISH_API_KEY;
```

## Testing

1. Test with mock success (current implementation)
2. Test with mock failure (change status to 401 in placeholder)
3. Test with real API integration
4. Handle edge cases (network errors, timeouts, etc.)

## Important Notes

- The `external_user_id` is generated when user signs up
- It's stored in localStorage under the user object
- The API call happens **after** password validation succeeds
- Only a 200 status allows dashboard access
- Any other status returns user to landing page
