/**
 * MediGuard Auth Helper
 * Uses Flask session cookies - no localStorage needed
 */

const API_ROOT = (window.MEDIGUARD_API_BASE || '').replace(/\/$/, '');
const AUTH_API = `${API_ROOT}/api`;

/**
 * Get current logged-in user from Flask session
 * Returns user object or null
 */
async function getCurrentUser() {
    try {
        const response = await fetch(`${AUTH_API}/user`, {
            method: 'GET',
            credentials: 'include',   // ✅ send session cookie
            headers: { 'Accept': 'application/json' }
        });

        if (response.status === 401 || response.status === 404) {
            return null;  // not logged in
        }

        if (!response.ok) {
            console.warn('Auth check failed:', response.status);
            return null;
        }

        const data = await response.json();
        return data.user || null;

    } catch (error) {
        console.warn('Could not check auth:', error);
        return null;
    }
}

/**
 * Login user
 */
async function loginUser(email, password) {
    try {
        const response = await fetch(`${AUTH_API}/login`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            return { success: true, user: data.user };
        } else {
            return { success: false, error: data.error || 'Login failed' };
        }
    } catch (error) {
        return { success: false, error: 'Network error. Is Flask running?' };
    }
}

/**
 * Register user
 */
async function registerUser(userData) {
    try {
        const response = await fetch(`${AUTH_API}/register`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            return { success: true, user: data.user };
        } else {
            return { success: false, error: data.error || 'Registration failed' };
        }
    } catch (error) {
        return { success: false, error: 'Network error. Is Flask running?' };
    }
}

/**
 * Logout user
 */
async function logoutUser() {
    try {
        await fetch(`${AUTH_API}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (e) {}
    window.location.href = '/login';
}