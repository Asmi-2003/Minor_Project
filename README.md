# PulseChat ⚡

A polished, real-time messaging application built with **Spring Boot 3**, **React + Vite**, **MongoDB**, and **WebSocket (STOMP over SockJS)**.

![PulseChat — Real-time messaging](https://img.shields.io/badge/PulseChat-Real--Time%20Chat-6366f1?style=for-the-badge&logo=lightning)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.4.2-brightgreen?style=flat-square&logo=spring)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square&logo=react)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47a248?style=flat-square&logo=mongodb)

---

## Features

| Feature | Description |
|---------|-------------|
| **User Authentication** | Signup & Login with Gmail/email and BCrypt password encryption |
| **Unique Email Rule** | Duplicate emails are strictly rejected (HTTP 409 Conflict) |
| **Create / Join rooms** | Create a private room or join one by ID via REST API |
| **Real-time messaging** | WebSocket (STOMP/SockJS) — messages delivered instantly |
| **Message persistence** | All messages saved to MongoDB; history loaded on join |
| **Live typing indicator** | See when others are typing (throttled, per-room, per-user) |
| **Live participant count** | Room header shows current online count (WebSocket session tracking) |
| **Connection status badge** | Clear visual of WebSocket state (connecting / connected / disconnected) |
| **Deduplication** | WebSocket message and REST history merged without duplicates |
| **Responsive UI** | Collapsible sidebar; works on mobile, tablet, desktop |
| **Toast notifications** | Non-blocking success / error / warning messages |
| **Avatar initials** | Deterministic colour-coded avatar per username |
| **Auto-scroll** | Stays at bottom; shows ↓ button when user scrolls up |

---

## Technology Stack

### Backend
| Technology | Version | Role |
|-----------|---------|------|
| Java | 21 | Language |
| Spring Boot | 3.4.2 | Application framework |
| Spring Web | — | REST API |
| Spring WebSocket | — | STOMP / SockJS real-time |
| Spring Data MongoDB | — | Persistence |
| Lombok | latest | Boilerplate reduction |
| Maven | Wrapper (mvnw) | Build tool |

### Frontend
| Technology | Version | Role |
|-----------|---------|------|
| React | 18 | UI library |
| Vite | 8 | Dev server + build tool |
| React Router | 7 | Client-side routing |
| @stomp/stompjs | 7 | STOMP WebSocket client |
| sockjs-client | 1.6 | SockJS transport |
| lucide-react | latest | Icons |
| CSS Modules | — | Scoped component styling |

### Database
| Technology | Role |
|-----------|------|
| MongoDB 7 (local) | Stores rooms and messages |

---

## Architecture & Message Flow

```
User Browser (React/Vite :5173)
        │
        │  REST (fetch)
        ├──────────────────────► POST /api/v1/rooms          Create room
        ├──────────────────────► GET  /api/v1/rooms/{id}     Join room / verify
        ├──────────────────────► GET  /api/v1/rooms/{id}/messages  History
        │
        │  WebSocket (STOMP/SockJS)
        ├──────────────────────► CONNECT  /chat
        ├─── SUBSCRIBE ────────► /topic/room/{roomId}          Receive messages
        ├─── SUBSCRIBE ────────► /topic/room/{roomId}/typing    Typing events
        ├─── SUBSCRIBE ────────► /topic/room/{roomId}/participants  Count updates
        │
        ├─── SEND ─────────────► /app/sendMessage/{roomId}    Send chat message
        ├─── SEND ─────────────► /app/typing/{roomId}         Typing indicator
        ├─── SEND ─────────────► /app/join/{roomId}           Announce join
        └─── SEND ─────────────► /app/leave/{roomId}          Announce leave

Spring Boot (:8080)
        │
        ├── ChatController      Handles STOMP messages; validates; persists; broadcasts
        ├── RoomController      REST endpoints
        ├── RoomParticipantService  In-memory ConcurrentHashMap session tracking
        ├── WebSocketEventListener  Cleans up on disconnect
        └── MongoDB             Stores Room documents with embedded Message list
```

---

## Prerequisites

| Requirement | Minimum Version | Check command |
|------------|----------------|---------------|
| Java JDK | 21 | `java -version` |
| Maven | wrapper included | `.\mvnw.cmd -v` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| MongoDB | 6+ | `mongod --version` |

MongoDB must be running locally on the default port **27017** before starting the backend.

---

## Quick Start

### 1. Start MongoDB

Make sure MongoDB is running. Common ways:

```powershell
# Windows — MongoDB as a service (if installed)
net start MongoDB

# Or run manually (adjust path to your MongoDB installation)
"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\data\db"
```

```bash
# macOS / Linux
mongod --dbpath /data/db

# Or if using Homebrew:
brew services start mongodb-community
```

> The `chatApp` database and `rooms` collection are created automatically on first use.

---

### 2. Start the Spring Boot Backend

```powershell
cd "chat-app-backend"
$env:MAVEN_USER_HOME = "D:\maven-home"
$env:MAVEN_USER_HOME = "D:\maven-home"
```

Wait for:
```
Started ChatAppBackendApplication in X seconds
```

Backend runs at **http://localhost:8081**

---

### 3. Start the React Frontend

Open a **new terminal**:

```powershell
cd "chat-app-frontend"
npm install          # only needed on first run
npm run dev
```

Frontend runs at **http://localhost:5173**

---

### 4. Open the App

Navigate to **http://localhost:5173** in your browser.

---

## Configuration

### Frontend — `.env`

```env
# chat-app-frontend/.env
VITE_API_BASE_URL=http://localhost:8081
VITE_WS_URL=http://localhost:8081/chat
```

Copy `.env.example` to `.env` if the file is missing.

### Backend — `application.properties`

```properties
spring.application.name=chat-app-backend
spring.data.mongodb.uri=mongodb://localhost:27017/chatApp
server.port=8080
spring.jackson.serialization.write-dates-as-timestamps=false
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `POST` | `/api/v1/auth/signup` | `{"name":"...","email":"...","password":"..."}` | `201 Created` | Register new user account |
| `POST` | `/api/v1/auth/login` | `{"email":"...","password":"..."}` | `200 OK` | Authenticate with email & password |

### Room Management

| Method | Endpoint | Body | Response | Description |
|--------|----------|------|----------|-------------|
| `POST` | `/api/v1/rooms` | `{"roomId":"my-room"}` | `201 Created` — Room JSON | Create room |
| `GET` | `/api/v1/rooms/{roomId}` | — | `200 OK` — Room JSON | Get room / join |
| `GET` | `/api/v1/rooms/{roomId}/messages` | — | `200 OK` — Message array | Get paginated messages |

#### Create Room — Request

```json
POST /api/v1/rooms
Content-Type: application/json

{ "roomId": "my-room-123" }
```

**Rules:** 3–50 characters; letters, numbers, hyphens, underscores only.

#### Create Room — Responses

| HTTP | Meaning |
|------|---------|
| `201 Created` | Room created successfully |
| `400 Bad Request` | Invalid `roomId` format |
| `409 Conflict` | Room already exists |

#### Get Messages — Pagination

```
GET /api/v1/rooms/{roomId}/messages?page=0&size=50
```

- `page=0` — most recent messages
- `page=1` — older messages
- Messages within each page are returned **oldest-first** (chronological)

---

## WebSocket Destinations

All WebSocket communication uses STOMP over SockJS.

**Connection endpoint:** `http://localhost:8081/chat`

### Subscriptions (client → server, then receive)

| Destination | Payload | Description |
|-------------|---------|-------------|
| `/topic/room/{roomId}` | `Message` JSON | Live chat messages |
| `/topic/room/{roomId}/typing` | `TypingEvent` JSON | Typing indicators |
| `/topic/room/{roomId}/participants` | `ParticipantEvent` JSON | Participant count updates |

### Sends (client → server)

| Destination | Payload | Description |
|-------------|---------|-------------|
| `/app/sendMessage/{roomId}` | `MessageRequest` JSON | Send a chat message |
| `/app/typing/{roomId}` | `TypingEvent` JSON | Notify typing state |
| `/app/join/{roomId}` | `MessageRequest` JSON | Register as participant |
| `/app/leave/{roomId}` | `MessageRequest` JSON | Deregister as participant |

### Payload Schemas

**MessageRequest** (send)
```json
{ "content": "Hello!", "sender": "Alice", "roomId": "my-room" }
```

**Message** (receive — from `/topic/room/{roomId}`)
```json
{ "sender": "Alice", "content": "Hello!", "time": "2025-01-01T12:00:00" }
```

**TypingEvent**
```json
{ "sender": "Alice", "roomId": "my-room", "typing": true }
```

**ParticipantEvent**
```json
{ "roomId": "my-room", "count": 3, "type": "JOIN", "username": "Alice" }
```

---

## Testing with Two Browser Windows

1. Open **http://localhost:5173** in Window 1. Enter username `Alice`, create room `test-room`.
2. Open **http://localhost:5173** in Window 2 (or use an Incognito window). Enter username `Bob`, join `test-room`.
3. Both windows should show participant count = 2.
4. Type a message in one window — it appears instantly in the other.
5. Start typing (without sending) — the other window shows the typing indicator.
6. Leave the room in one window — participant count updates in the other.

---

## Backend Test Suite

```powershell
cd "chat-app-backend"
.\mvnw.cmd test
```

**Result (last run):** Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 — **BUILD SUCCESS**

The test verifies the full Spring application context loads with all beans (WebSocket config, CORS config, controllers, services) correctly wired.

---

## Frontend Production Build

```powershell
cd "chat-app-frontend"
npm run build
```

**Result (last run):** `✓ built in 1.32s` — zero errors. Output in `dist/`.

To serve the production build:
```powershell
npm run preview
```

---

## Project Structure

```
chat App/
├── chat-app-backend/
│   ├── pom.xml
│   └── src/main/java/com/chatApp_backend/chat_app_backend/
│       ├── ChatAppBackendApplication.java
│       ├── config/
│       │   ├── CorsConfig.java              # Global CORS filter
│       │   ├── HttpHandshakeInterceptor.java # WebSocket handshake
│       │   ├── WebSocketEventListener.java   # Disconnect cleanup
│       │   └── WebsocketConfig.java          # STOMP broker config
│       ├── controller/
│       │   ├── ChatController.java           # STOMP message handlers
│       │   └── RoomController.java           # REST endpoints
│       ├── dto/
│       │   ├── MessageRequest.java
│       │   ├── ParticipantEvent.java
│       │   └── TypingEvent.java
│       ├── entities/
│       │   ├── Message.java                  # Embedded in Room
│       │   └── Room.java                     # MongoDB @Document
│       ├── repo/
│       │   └── RoomRepo.java                 # MongoRepository
│       └── service/
│           └── RoomParticipantService.java   # In-memory session tracking
│
└── chat-app-frontend/
    ├── .env                    # VITE_API_BASE_URL, VITE_WS_URL
    ├── .env.example
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx             # Router setup
        ├── api/
        │   └── roomApi.js      # Centralized REST API client
        ├── components/
        │   ├── Avatar.jsx      # Deterministic colour-coded avatars
        │   ├── ConnectionBadge.jsx  # WS status badge
        │   ├── MessageBubble.jsx    # Chat message bubble
        │   ├── Toast.jsx            # Toast notification system
        │   └── TypingIndicator.jsx  # Animated typing dots
        ├── hooks/
        │   ├── useStompClient.js     # WebSocket connection + subscriptions
        │   └── useTypingIndicator.js # Throttled typing events
        ├── pages/
        │   ├── ChatPage.jsx          # Main chatroom
        │   └── LandingPage.jsx       # Landing + room access
        └── styles/
            └── global.css            # Design system (CSS variables, reset)
```

---

## Known Limitations

1. **No authentication** — Usernames are display names only; anyone can claim any name.
2. **Single server** — In-memory participant tracking; not distributed.
3. **Participant count** — Tracks WebSocket sessions, not unique users.  If the same user connects from two tabs, they count as 2.
4. **Message history** — All messages are stored inside the Room document in MongoDB (embedded). Very large rooms with thousands of messages may slow document reads. For production, use a separate Message collection with indexed queries.
5. **No file / image sharing**.
6. **Typing indicator cleanup** — Server has no cleanup mechanism; done via client-side timeouts.

---

## Troubleshooting

### "Cannot connect to server. Is the backend running on port 8080?"
- Ensure `mvnw.cmd spring-boot:run` is running in `chat-app-backend/`.
- Check port 8080 is not in use: `netstat -ano | findstr :8080`

### MongoDB connection errors on startup
- Start MongoDB first: `net start MongoDB` or `mongod --dbpath C:\data\db`
- Verify connection: `mongosh mongodb://localhost:27017`

### "Room not found" when joining
- The room ID is case-sensitive. Use the exact ID shown after creation.

### WebSocket not connecting (stuck on "Connecting…")
- Check the browser console for CORS errors.
- Ensure the backend is running and `VITE_WS_URL` in `.env` matches the backend port.
- Clear browser cache and hard-reload (Ctrl+Shift+R).

### Port conflicts
- Backend default: **8080** — change `server.port` in `application.properties`
- Frontend default: **5173** — change `server.port` in `vite.config.js`
- Update `VITE_API_BASE_URL` and `VITE_WS_URL` in `.env` if backend port changes.
- Update `setAllowedOrigins` in `WebsocketConfig.java` and `CorsConfig.java` if frontend port changes.

