/**
 * OWASP BLT - Main Application Module
 */
// ===================================
// Configuration    
// Configuration    
// ===================================
const CONFIG = {
    // API endpoint - should be set to your Cloudflare Worker URL
    // For production, use absolute URL like: 'https://api.owaspblt.org'
    // For local development with worker: 'http://localhost:8787'
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8787'
        : 'https://api.owaspblt.org', // TODO: Replace with your actual worker URL
    CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
    ENABLE_ANALYTICS: true,
};

// ===================================
// State Management
// ===================================
class AppState {
    constructor() {
        this.user = null;
        this.isAuthenticated = false;
        this.listeners = new Map();
    }

    subscribe(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    emit(event, data) {
        const callbacks = this.listeners.get(event) || [];
        callbacks.forEach(callback => callback(data));
    }

    setUser(user) {
        this.user = user;
        this.isAuthenticated = !!user;
        this.emit('user:changed', user);
    }

    getUser() {
        return this.user;
    }
}

const state = new AppState();

// ===================================
// API Client
// ===================================
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.cache = new Map();
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // Add auth token if available
        const token = localStorage.getItem('authToken');
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async get(endpoint, useCache = false) {
        if (useCache && this.cache.has(endpoint)) {
            const cached = this.cache.get(endpoint);
            if (Date.now() - cached.timestamp < CONFIG.CACHE_DURATION) {
                return cached.data;
            }
        }

        const data = await this.request(endpoint, { method: 'GET' });

        if (useCache) {
            this.cache.set(endpoint, {
                data,
                timestamp: Date.now(),
            });
        }

        return data;
    }

    async post(endpoint, body) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    async put(endpoint, body) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body),
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    }

    clearCache() {
        this.cache.clear();
    }
}

const api = new APIClient(CONFIG.API_BASE_URL);

// ===================================
// Authentication Module
// ===================================
class AuthModule {
    constructor(apiClient, appState) {
        this.api = apiClient;
        this.state = appState;
    }

    async login(email, password) {
        try {
            const response = await this.api.post('/auth/login', { email, password });

            if (response.token) {
                localStorage.setItem('authToken', response.token);
                this.state.setUser(response.user);
                return { success: true, user: response.user };
            }

            return { success: false, error: 'Invalid credentials' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async signup(userData) {
        try {
            const response = await this.api.post('/auth/signup', userData);

            if (response.token) {
                localStorage.setItem('authToken', response.token);
                this.state.setUser(response.user);
                return { success: true, user: response.user };
            }

            return { success: false, error: 'Signup failed' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async logout() {
        try {
            await this.api.post('/auth/logout', {});
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('authToken');
            this.state.setUser(null);
            this.api.clearCache();
        }
    }

    async checkAuth() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            return false;
        }

        try {
            const response = await this.api.get('/auth/me');
            if (response.user) {
                this.state.setUser(response.user);
                return true;
            }
        } catch (error) {
            // Token invalid, clear it
            localStorage.removeItem('authToken');
        }

        return false;
    }
}

const auth = new AuthModule(api, state);

// ===================================
// UI Components
// ===================================
class UIComponents {
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 0.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// ===================================
// Event Handlers
// ===================================
function setupEventHandlers() {
    // Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');

    function updateThemeIcons() {
        if (!sunIcon || !moonIcon) return;
        if (document.documentElement.classList.contains('dark')) {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        } else {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        }
    }

    if (themeToggle) {
        // Initial icon state
        updateThemeIcons();

        themeToggle.addEventListener('click', () => {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateThemeIcons();

            // Re-emit theme change for other components
            if (window.bltApp && window.bltApp.state) {
                window.bltApp.state.emit('theme:changed', isDark ? 'dark' : 'light');
            }
        });
    }
}

// ===================================
// UI Updates
// ===================================
function updateUIForAuth() {
    const user = state.getUser();
    const loginBtn = document.getElementById('loginBtn');
    const signupBtn = document.getElementById('signupBtn');

    if (user && state.isAuthenticated) {
        // Update buttons to show user menu
        if (loginBtn) {
            loginBtn.textContent = user.username;
            loginBtn.onclick = () => {
                window.location.href = '/pages/profile.html';
            };
        }
        if (signupBtn) {
            signupBtn.textContent = 'Logout';
            signupBtn.classList.remove('btn-primary');
            signupBtn.classList.add('btn-secondary');
            signupBtn.onclick = async () => {
                await auth.logout();
                UIComponents.showNotification('Logged out successfully', 'success');
                updateUIForAuth();
            };
        }
    }
}

// ===================================
// Footer Last Updated
// ===================================
function updateFooterLastUpdated() {
    const el = document.getElementById('footer-last-updated');
    if (!el) return;

    const lastModified = new Date(document.lastModified);
    const now = new Date();
    const diffMins = Math.max(0, Math.floor((now - lastModified) / 60000));
    const hours = Math.floor(diffMins / 60);
    const mins = diffMins % 60;

    const dateStr = lastModified.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
    });

    let agoStr;
    if (hours > 0 && mins > 0) {
        agoStr = `${hours} hour${hours !== 1 ? 's' : ''} and ${mins} minute${mins !== 1 ? 's' : ''} ago`;
    } else if (hours > 0) {
        agoStr = `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else if (mins > 0) {
        agoStr = `${mins} minute${mins !== 1 ? 's' : ''} ago`;
    } else {
        agoStr = 'just now';
    }

    el.textContent = `Last updated: ${dateStr} (${agoStr})`;
}

// ===================================
// Initialization
// ===================================
async function init() {
    // Setup event handlers immediately so UI is responsive
    try {
        setupEventHandlers();
    } catch (error) {
        // Silently fail or log sparingly in production
    }

    // Check authentication status in background
    try {
        await auth.checkAuth();
        updateUIForAuth();
    } catch (error) {
        // Auth check failure is handled by UI state
    }

    // Update footer with last modified date
    updateFooterLastUpdated();

    // Update state to ready
    state.emit('app:ready');

    // Add CSS animations
    if (!document.getElementById('blt-animations')) {
        const style = document.createElement('style');
        style.id = 'blt-animations';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// ===================================
// Export to window for global access
// ===================================
window.bltApp = {
    state,
    api,
    auth,
};

window.uiComponents = UIComponents;

// ===================================
// Start the application
// ===================================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
