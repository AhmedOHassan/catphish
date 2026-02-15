/**
 * Authentication Service
 * Handles user authentication using localStorage
 */

const USERS_KEY = 'securebank_users';
const CURRENT_USER_KEY = 'securebank_current_user';

/**
 * Generate a unique user ID
 */
function generateUserId() {
  return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Get all users from localStorage
 */
function getUsers() {
  const users = localStorage.getItem(USERS_KEY);
  return users ? JSON.parse(users) : [];
}

/**
 * Save users to localStorage
 */
function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

/**
 * Sign up a new user
 * @param {string} email 
 * @param {string} password 
 * @returns {{success: boolean, message: string, user?: object}}
 */
export function signUp(email, password) {
  const users = getUsers();
  
  // Check if user already exists
  if (users.find(u => u.email === email)) {
    return {
      success: false,
      message: 'User with this email already exists'
    };
  }

  // Create new user
  const newUser = {
    id: generateUserId(),
    email,
    password // ⚠️ In production, NEVER store plain passwords!
  };

  users.push(newUser);
  saveUsers(users);

  return {
    success: true,
    message: 'Account created successfully',
    user: { id: newUser.id, email: newUser.email }
  };
}

/**
 * Login a user
 * @param {string} email 
 * @param {string} password 
 * @returns {{success: boolean, message: string, user?: object}}
 */
export function login(email, password) {
  const users = getUsers();
  const user = users.find(u => u.email === email && u.password === password);

  if (!user) {
    return {
      success: false,
      message: 'Invalid email or password'
    };
  }

  return {
    success: true,
    message: 'Login successful',
    user: { id: user.id, email: user.email }
  };
}

/**
 * Save current logged-in user
 */
export function setCurrentUser(user) {
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
}

/**
 * Get current logged-in user
 */
export function getCurrentUser() {
  const user = localStorage.getItem(CURRENT_USER_KEY);
  return user ? JSON.parse(user) : null;
}

/**
 * Logout current user
 */
export function logout() {
  localStorage.removeItem(CURRENT_USER_KEY);
  // Also clear Catphish external_user_id to prevent ID reuse across different accounts
  localStorage.removeItem('external_user_id');
  localStorage.removeItem('catphish_return_url');
}

/**
 * Check if user is logged in
 */
export function isLoggedIn() {
  return getCurrentUser() !== null;
}
