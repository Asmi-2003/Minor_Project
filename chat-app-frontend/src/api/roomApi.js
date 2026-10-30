/**
 * Centralized API utility for PulseChat.
 * All REST calls to the Spring Boot backend go through here.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8081'

class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.status = status
    this.data = data
    this.name = 'ApiError'
  }
}

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
    const text = await response.text()
    let data
    try { data = JSON.parse(text) } catch { data = text }

    if (!response.ok) {
      const message =
        (data && typeof data === 'object' && data.error) ||
        (typeof data === 'string' && data) ||
        `HTTP ${response.status}`
      throw new ApiError(message, response.status, data)
    }
    return data
  } catch (err) {
    if (err instanceof ApiError) throw err
    if (err.name === 'TypeError') {
      throw new ApiError(
        'Cannot connect to server. Is the backend running on port 8080?',
        0,
        null
      )
    }
    throw err
  }
}

export const roomApi = {
  /**
   * Create a new room.
   * POST /api/v1/rooms  — sends JSON { roomId: "..." }
   */
  createRoom: (roomId) =>
    request('/api/v1/rooms', {
      method: 'POST',
      body: JSON.stringify({ roomId }),
    }),

  /**
   * Join / verify room existence.
   * GET /api/v1/rooms/{roomId}
   */
  joinRoom: (roomId) => request(`/api/v1/rooms/${roomId}`),

  /**
   * Get paginated messages.
   * GET /api/v1/rooms/{roomId}/messages?page=0&size=50
   */
  getMessages: (roomId, page = 0, size = 50) =>
    request(`/api/v1/rooms/${roomId}/messages?page=${page}&size=${size}`),

  /**
   * Get active participant usernames in a room.
   * GET /api/v1/rooms/{roomId}/participants
   */
  getParticipants: (roomId) =>
    request(`/api/v1/rooms/${roomId}/participants`),
}

export { ApiError }
