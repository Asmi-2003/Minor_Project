import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { roomApi } from '../api/roomApi'
import { useStompClient } from '../hooks/useStompClient'
import { useTypingIndicator } from '../hooks/useTypingIndicator'
import { useToast } from '../components/Toast'
import { useAuth } from '../context/AuthContext'
import { MessageBubble } from '../components/MessageBubble'
import { TypingIndicator } from '../components/TypingIndicator'
import { ConnectionBadge } from '../components/ConnectionBadge'
import { Avatar } from '../components/Avatar'
import {
  LogOut, Users, Hash, Send, ChevronUp, MessageSquare,
  Zap, Menu, X, AlertCircle
} from 'lucide-react'
import styles from './ChatPage.module.css'

const MESSAGES_PER_PAGE = 50

export default function ChatPage() {
  const { roomId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const { addToast } = useToast()
  const { user } = useAuth()

  // Get username from location state, fall back to localStorage
  const [username] = useState(() => {
    return location.state?.username || localStorage.getItem('pulsechat_username') || ''
  })

  // Redirect if no username
  useEffect(() => {
    if (!username) {
      addToast('Please enter a username first', 'warning')
      navigate('/', { replace: true })
    } else {
      localStorage.setItem('pulsechat_username', username)
    }
  }, [username, navigate, addToast])

  // State
  const [messages, setMessages] = useState([])
  const [messagesLoading, setMessagesLoading] = useState(true)
  const [messagesError, setMessagesError] = useState(null)
  const [messageInput, setMessageInput] = useState('')
  const [sending, setSending] = useState(false)
  const [typingUsers, setTypingUsers] = useState({}) // { username: timestamp }
  const [participantCount, setParticipantCount] = useState(0)
  const [participants, setParticipants] = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [seenMessageIds, setSeenMessageIds] = useState(new Set())

  // Scroll
  const messagesEndRef = useRef(null)
  const scrollContainerRef = useRef(null)
  const [autoScroll, setAutoScroll] = useState(true)
  const userScrolledUpRef = useRef(false)

  // Clean up typing indicators after timeout
  const typingCleanupRef = useRef({})

  // --- Load initial message history ---
  useEffect(() => {
    if (!roomId || !username) return

    async function loadMessages() {
      setMessagesLoading(true)
      setMessagesError(null)
      try {
        const [msgsData, partsData] = await Promise.all([
          roomApi.getMessages(roomId, 0, MESSAGES_PER_PAGE),
          roomApi.getParticipants(roomId).catch(() => [])
        ])

        const msgs = Array.isArray(msgsData) ? msgsData : []
        setMessages(msgs)
        const ids = new Set(msgs.map(m => msgKey(m)))
        setSeenMessageIds(ids)

        const rawParts = Array.isArray(partsData) ? partsData : []
        const merged = Array.from(new Set([...rawParts, username]))
        setParticipants(merged)
        setParticipantCount(merged.length)
      } catch (err) {
        setMessagesError(err.message || 'Failed to load messages')
        addToast('Failed to load message history', 'error')
        if (err.status === 404) {
          navigate('/', { replace: true })
        }
      } finally {
        setMessagesLoading(false)
      }
    }
    loadMessages()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId])

  // --- WebSocket message handlers ---
  const handleMessage = useCallback((msg) => {
    const key = msgKey(msg)
    setSeenMessageIds(prev => {
      if (prev.has(key)) return prev // deduplicate
      const next = new Set(prev)
      next.add(key)
      return next
    })
    setMessages(prev => {
      if (prev.some(m => msgKey(m) === key)) return prev
      return [...prev, msg]
    })
  }, [])

  const handleTyping = useCallback((event) => {
    if (!event || event.sender === username) return // Don't show own typing indicator

    const { sender, typing } = event

    // Clear existing cleanup timer
    clearTimeout(typingCleanupRef.current[sender])

    if (typing) {
      setTypingUsers(prev => ({ ...prev, [sender]: Date.now() }))
      // Auto-clear after 3 seconds
      typingCleanupRef.current[sender] = setTimeout(() => {
        setTypingUsers(prev => {
          const next = { ...prev }
          delete next[sender]
          return next
        })
      }, 3000)
    } else {
      setTypingUsers(prev => {
        const next = { ...prev }
        delete next[sender]
        return next
      })
    }
  }, [username])

  const handleParticipants = useCallback((event) => {
    if (!event) return

    if (event.count !== undefined) {
      setParticipantCount(event.count)
    }

    if (Array.isArray(event.users) && event.users.length > 0) {
      setParticipants(event.users)
    } else if (event.username) {
      setParticipants(prev => {
        if (event.type === 'JOIN') {
          return Array.from(new Set([...prev, event.username]))
        } else if (event.type === 'LEAVE') {
          return prev.filter(u => u !== event.username)
        }
        return prev
      })
    }

    // When another participant joins or leaves, display notification and chat announcement
    if (event.username && event.username !== username) {
      const isJoin = event.type === 'JOIN'
      const actionText = isJoin ? 'joined the room' : 'left the room'
      addToast(`${event.username} ${actionText}`, isJoin ? 'info' : 'warning', 3000)

      setMessages(prev => [
        ...prev,
        {
          isSystem: true,
          content: `${event.username} ${actionText}`,
          time: new Date().toISOString(),
          type: event.type,
          sender: 'system'
        }
      ])
    }
  }, [username, addToast])

  const handleConnect = useCallback(() => {
    addToast('Connected to chat', 'success', 2000)
  }, [addToast])

  const handleDisconnect = useCallback(() => {
    addToast('Disconnected from chat', 'warning')
  }, [addToast])

  const { connected, connectionStatus, sendMessage, sendTyping, disconnect } =
    useStompClient({
      roomId,
      username,
      onMessage: handleMessage,
      onTyping: handleTyping,
      onParticipants: handleParticipants,
      onConnect: handleConnect,
      onDisconnect: handleDisconnect,
    })

  const { handleTypingStart, handleTypingStop } = useTypingIndicator(sendTyping)

  // --- Scroll management ---
  function scrollToBottom(smooth = true) {
    messagesEndRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'instant' })
  }

  // Auto-scroll on new message if user hasn't scrolled up
  useEffect(() => {
    if (autoScroll) {
      scrollToBottom(messages.length > 1)
    }
  }, [messages, autoScroll])

  // Detect if user has scrolled up
  function handleScroll() {
    const el = scrollContainerRef.current
    if (!el) return
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100
    userScrolledUpRef.current = !isNearBottom
    setAutoScroll(isNearBottom)
  }

  // --- Send message ---
  async function handleSend() {
    const content = messageInput.trim()
    if (!content) return
    if (!connected) {
      addToast('Not connected. Please wait…', 'warning')
      return
    }

    setSending(true)
    handleTypingStop()
    const ok = sendMessage(content)
    if (ok) {
      setMessageInput('')
    } else {
      addToast('Failed to send message', 'error')
    }
    setSending(false)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleInputChange(e) {
    setMessageInput(e.target.value)
    if (e.target.value) {
      handleTypingStart()
    } else {
      handleTypingStop()
    }
  }

  // --- Leave room ---
  function handleLeave() {
    disconnect()
    navigate('/', { replace: true })
  }

  // Typing users list (sorted, excluding stale)
  const activeTypingUsers = Object.keys(typingUsers)

  return (
    <div className={styles.layout}>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className={styles.sidebarOverlay}
          onClick={() => setSidebarOpen(false)}
          aria-hidden
        />
      )}

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ''}`}>
        <div className={styles.sidebarHeader}>
          <div className={styles.sidebarLogo}>
            <div className={styles.logoIcon}>
              <Zap size={18} />
            </div>
            <span className={styles.logoText}>PulseChat</span>
          </div>
          <button
            className={styles.closeSidebarBtn}
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={18} />
          </button>
        </div>

        <div className={styles.sidebarContent}>
          {/* Room info */}
          <div className={styles.sidebarSection}>
            <p className={styles.sidebarSectionLabel}>Current Room</p>
            <div className={styles.roomInfo}>
              <div className={styles.roomInfoIcon}>
                <Hash size={16} />
              </div>
              <div className={styles.roomInfoText}>
                <p className={styles.roomId}>{roomId}</p>
                <p className={styles.roomMeta}>Room ID</p>
              </div>
            </div>
          </div>

          {/* You */}
          <div className={styles.sidebarSection}>
            <p className={styles.sidebarSectionLabel}>You</p>
            <div className={styles.userInfo}>
              <Avatar username={username} size={34} />
              <div>
                <p className={styles.username}>{username}</p>
                <p className={styles.userMeta}>{user?.email || 'Display name'}</p>
              </div>
            </div>
          </div>

          {/* Participants */}
          <div className={styles.sidebarSection}>
            <div className={styles.participantsHeader}>
              <p className={styles.sidebarSectionLabel}>Online ({participants.length || participantCount})</p>
              <div className={styles.participantCountBadge}>
                <Users size={13} />
                <span>{participants.length || participantCount}</span>
              </div>
            </div>

            <div className={styles.participantsList}>
              {(participants.length > 0 ? participants : [username]).map((userItem) => (
                <div key={userItem} className={styles.participantItem}>
                  <div className={styles.avatarWrapperWithDot}>
                    <Avatar username={userItem} size={28} />
                    <span className={styles.onlineDot} title="Online" />
                  </div>
                  <div className={styles.participantDetails}>
                    <span className={styles.participantUsername}>
                      {userItem}
                    </span>
                    {userItem === username && (
                      <span className={styles.youPill}>You</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Connection status */}
          <div className={styles.sidebarSection}>
            <p className={styles.sidebarSectionLabel}>Connection</p>
            <ConnectionBadge status={connectionStatus} />
          </div>
        </div>

        <div className={styles.sidebarFooter}>
          <button className={styles.leaveBtn} onClick={handleLeave}>
            <LogOut size={16} />
            <span>Leave Room</span>
          </button>
        </div>
      </aside>

      {/* Main chat area */}
      <div className={styles.chatArea}>
        {/* Chat header */}
        <header className={styles.chatHeader}>
          <div className={styles.chatHeaderLeft}>
            <button
              className={styles.menuBtn}
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
            >
              <Menu size={20} />
            </button>
            <div className={styles.headerRoomInfo}>
              <div className={styles.headerRoomIcon}>
                <Hash size={16} />
              </div>
              <div>
                <h1 className={styles.headerRoomId}>{roomId}</h1>
                <div className={styles.headerMeta}>
                  <Users size={12} />
                  <span>{participantCount} online</span>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.chatHeaderRight}>
            <ConnectionBadge status={connectionStatus} />
            <button className={styles.leaveBtnHeader} onClick={handleLeave} title="Leave room">
              <LogOut size={16} />
            </button>
          </div>
        </header>

        {/* Messages area */}
        <div
          className={styles.messagesContainer}
          ref={scrollContainerRef}
          onScroll={handleScroll}
        >
          {messagesLoading ? (
            <div className={styles.loadingState}>
              <div className={styles.spinner} />
              <p>Loading messages…</p>
            </div>
          ) : messagesError ? (
            <div className={styles.errorState}>
              <AlertCircle size={32} />
              <p>{messagesError}</p>
              <button onClick={() => window.location.reload()} className={styles.retryBtn}>
                Retry
              </button>
            </div>
          ) : messages.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>
                <MessageSquare size={40} />
              </div>
              <h3>No messages yet</h3>
              <p>Be the first to say something in <strong>#{roomId}</strong></p>
            </div>
          ) : (
            <div className={styles.messagesList}>
              {messages.map((msg, i) => (
                msg.isSystem ? (
                  <div key={`sys-${i}-${msg.time}`} className={styles.systemMessageRow}>
                    <span className={styles.systemMessagePill}>
                      {msg.type === 'JOIN' ? '👋 ' : '🚪 '}
                      <strong>{msg.content}</strong>
                    </span>
                  </div>
                ) : (
                  <MessageBubble
                    key={`${i}-${msgKey(msg)}`}
                    message={msg}
                    isOwn={msg.sender === username}
                  />
                )
              ))}
            </div>
          )}

          {/* Typing indicator */}
          {activeTypingUsers.length > 0 && (
            <TypingIndicator typingUsers={activeTypingUsers} />
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Scroll to bottom button */}
        {!autoScroll && (
          <button
            className={styles.scrollBottomBtn}
            onClick={() => { setAutoScroll(true); scrollToBottom() }}
            aria-label="Scroll to bottom"
          >
            <ChevronUp size={18} style={{ transform: 'rotate(180deg)' }} />
          </button>
        )}

        {/* Message composer */}
        <div className={styles.composer}>
          <div className={`${styles.composerInput} ${!connected ? styles.composerDisabled : ''}`}>
            <textarea
              className={styles.textarea}
              placeholder={connected ? `Message #${roomId}…` : 'Connecting…'}
              value={messageInput}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              disabled={!connected || sending}
              rows={1}
              maxLength={2000}
            />
            <button
              className={`${styles.sendBtn} ${(!connected || !messageInput.trim() || sending) ? styles.sendBtnDisabled : ''}`}
              onClick={handleSend}
              disabled={!connected || !messageInput.trim() || sending}
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </div>
          <p className={styles.composerHint}>
            Enter to send &middot; Shift+Enter for new line
            {messageInput.length > 1800 && (
              <span className={styles.charCount}> {messageInput.length}/2000</span>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}

/** Generates a deduplication key for a message */
function msgKey(m) {
  return `${m.sender}|${m.time}|${(m.content || '').slice(0, 40)}`
}
