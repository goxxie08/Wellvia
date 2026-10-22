/**
 * Central API Client for Wellvia React Frontend
 * Automatically includes credentials (cookies) for Flask session management.
 */

export async function apiRequest(endpoint, options = {}) {
  const defaultHeaders = {
    'Accept': 'application/json',
  };

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
    credentials: 'include', // Crucial for Flask session cookies
  };

  try {
    const response = await fetch(endpoint, config);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMsg = data.error || data.message || `Request failed with status ${response.status}`;
      const error = new Error(errorMsg);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (err) {
    console.error(`[API Error] ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Auth
  getMe: () => apiRequest('/api/auth/me'),
  login: (credentials) => apiRequest('/api/auth/login', { method: 'POST', body: credentials }),
  register: (userData) => apiRequest('/api/auth/register', { method: 'POST', body: userData }),
  logout: () => apiRequest('/api/auth/logout', { method: 'POST' }),
  forgotPassword: (email) => apiRequest('/api/auth/forgot-password', { method: 'POST', body: { email } }),

  // Student
  getDashboard: () => apiRequest('/api/student/dashboard'),
  getBodyMetrics: () => apiRequest('/api/student/body-metrics'),
  saveBodyMetrics: (payload) => apiRequest('/api/student/body-metrics', { method: 'POST', body: payload }),
  getTodayWellness: () => apiRequest('/api/student/wellness/today'),
  logWellness: (data) => apiRequest('/api/student/wellness', { method: 'POST', body: data }),
  getWellnessHistory: () => apiRequest('/api/student/wellness/history'),
  getTips: (category) => apiRequest(`/api/student/tips${category ? `?category=${encodeURIComponent(category)}` : ''}`),
  getChallenges: () => apiRequest('/api/student/challenges'),
  completeChallenge: (id) => apiRequest(`/api/student/challenges/${id}/complete`, { method: 'POST' }),
  getProgress: (days = 7) => apiRequest(`/api/student/progress?days=${days}`),
  getProfile: () => apiRequest('/api/student/profile'),

  // Admin
  getAdminAnalytics: () => apiRequest('/api/admin/analytics'),
  getAdminUsers: () => apiRequest('/api/admin/users'),
  toggleUser: (id) => apiRequest(`/api/admin/users/${id}/toggle`, { method: 'POST' }),
  getAdminTips: () => apiRequest('/api/admin/tips'),
  createAdminTip: (tip) => apiRequest('/api/admin/tips', { method: 'POST', body: tip }),
  deleteAdminTip: (id) => apiRequest(`/api/admin/tips/${id}`, { method: 'DELETE' }),
  getAdminChallenges: () => apiRequest('/api/admin/challenges'),
  createAdminChallenge: (ch) => apiRequest('/api/admin/challenges', { method: 'POST', body: ch }),
  toggleAdminChallenge: (id) => apiRequest(`/api/admin/challenges/${id}/toggle`, { method: 'POST' }),
  deleteAdminChallenge: (id) => apiRequest(`/api/admin/challenges/${id}`, { method: 'DELETE' }),

  // AI Chat
  sendChatMessage: (message, history = []) =>
    apiRequest('/api/chat/message', {
      method: 'POST',
      body: history && history.length > 0 ? { message, history } : { message }
    })
};
