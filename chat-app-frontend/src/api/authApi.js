/**
 * Centralized Authentication API utility for PulseChat.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8081'

class AuthError extends Error {
  constructor(message, status, data) {
    super(message)
    this.status = status
    this.data = data
    this.name = 'AuthError'
  }
}

async function authRequest(path, payload) {
  const url = `${BASE_URL}${path}`
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const text = await response.text()
    let data
    try { data = JSON.parse(text) } catch { data = text }

    if (!response.ok) {
      const message =
        (data && typeof data === 'object' && data.error) ||
        (typeof data === 'string' && data) ||
        `HTTP ${response.status}`
      throw new AuthError(message, response.status, data)
    }
    return data
  } catch (err) {
    if (err instanceof AuthError) throw err
    if (err.name === 'TypeError') {
      throw new AuthError('Cannot connect to authentication server. Is the backend running?', 0, null)
    }
    throw err
  }
}

export const authApi = {
  signup: ({ name, email, password }) =>
    authRequest('/api/v1/auth/signup', { name, email, password }),

  login: ({ email, password }) =>
    authRequest('/api/v1/auth/login', { email, password }),
}

export { AuthError }

