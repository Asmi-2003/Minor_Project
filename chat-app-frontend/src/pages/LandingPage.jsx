import { useState, useId } from 'react'
import { useNavigate } from 'react-router-dom'
import { roomApi } from '../api/roomApi'
import { useToast } from '../components/Toast'
import { useAuth } from '../context/AuthContext'
import { AuthCard } from '../components/AuthCard'
import { Avatar } from '../components/Avatar'
import styles from './LandingPage.module.css'
import {
  MessageSquare, Hash, User, Plus, ArrowRight, Zap,
  RefreshCw, Sparkles, LogOut, CheckCircle2
} from 'lucide-react'

function generateRoomId() {
  const adjectives = ['swift', 'bright', 'calm', 'bold', 'keen', 'vivid', 'epic', 'prime']
  const nouns = ['pulse', 'wave', 'echo', 'nova', 'surge', 'spark', 'orbit', 'nexus']
  const adj = adjectives[Math.floor(Math.random() * adjectives.length)]
  const noun = nouns[Math.floor(Math.random() * nouns.length)]
  const num = Math.floor(Math.random() * 900) + 100
  return `${adj}-${noun}-${num}`
}

function InputField({ label, id, placeholder, value, onChange, icon: Icon, error, hint, maxLength }) {
  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>{label}</label>
      <div className={`${styles.inputWrapper} ${error ? styles.inputError : ''}`}>
        {Icon && <Icon size={16} className={styles.inputIcon} />}
        <input
          id={id}
          className={styles.input}
          placeholder={placeholder}
          value={value}
          onChange={e => onChange(e.target.value)}
          maxLength={maxLength || 50}
          autoComplete="off"
          spellCheck={false}
        />
      </div>
      {error && <p className={styles.errorMsg}>{error}</p>}
      {hint && !error && <p className={styles.hint}>{hint}</p>}
    </div>
  )
}

export default function LandingPage() {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const { user, isAuthenticated, logout } = useAuth()

  const [mode, setMode] = useState(null) // null | 'create' | 'join'
  const [roomId, setRoomId] = useState('')
  const [guestName, setGuestName] = useState('')
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const usernameId = useId()
  const roomId_id = useId()

  const activeUsername = isAuthenticated ? user.name : guestName

  function validate() {
    const errs = {}
    if (!isAuthenticated) {
      if (!guestName.trim()) errs.username = 'Display name is required'
      else if (guestName.trim().length < 2) errs.username = 'Name must be at least 2 characters'
      else if (guestName.trim().length > 30) errs.username = 'Name is too long (max 30)'
    }

    if (!roomId.trim()) errs.roomId = 'Room ID is required'
    else if (roomId.trim().length < 3) errs.roomId = 'Room ID must be at least 3 characters'
    else if (!/^[a-zA-Z0-9_\-]+$/.test(roomId.trim())) errs.roomId = 'Only letters, numbers, hyphens, underscores'
    return errs
  }

  async function handleCreate() {
    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    try {
      await roomApi.createRoom(roomId.trim())
      addToast(`Room "${roomId.trim()}" created!`, 'success')
      navigate(`/chat/${roomId.trim()}`, { state: { username: activeUsername.trim() } })
    } catch (err) {
      if (err.status === 409) {
        addToast('Room already exists — try joining it instead.', 'warning')
        setErrors(prev => ({ ...prev, roomId: 'This room ID is already taken' }))
      } else {
        addToast(err.message || 'Failed to create room', 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleJoin() {
    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    try {
      await roomApi.joinRoom(roomId.trim())
      addToast(`Joined room "${roomId.trim()}"`, 'success')
      navigate(`/chat/${roomId.trim()}`, { state: { username: activeUsername.trim() } })
    } catch (err) {
      if (err.status === 404 || err.status === 400) {
        setErrors(prev => ({ ...prev, roomId: 'Room not found. Check the ID or create a new room.' }))
        addToast('Room not found', 'error')
      } else {
        addToast(err.message || 'Failed to join room', 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  function handleGenerate() {
    setRoomId(generateRoomId())
    setErrors(prev => ({ ...prev, roomId: undefined }))
  }

  function handleModeSwitch(newMode) {
    setMode(newMode)
    setErrors({})
    if (newMode === 'create') setRoomId(generateRoomId())
    else setRoomId('')
  }

  function handleLogout() {
    logout()
    setMode(null)
    addToast('Logged out successfully', 'info')
  }

  return (
    <div className={styles.page}>
      {/* Background decoration */}
      <div className={styles.bgOrb1} aria-hidden />
      <div className={styles.bgOrb2} aria-hidden />
      <div className={styles.bgGrid} aria-hidden />

      <main className={styles.main}>
        {/* Hero section */}
        <div className={styles.hero}>
          <div className={styles.logoRow}>
            <div className={styles.logoIcon}>
              <Zap size={26} />
            </div>
            <span className={styles.logoText}>PulseChat</span>
          </div>

          <h1 className={styles.headline}>
            Real-time conversations,{' '}
            <span className={styles.headlineAccent}>instantly connected</span>
          </h1>
          <p className={styles.subheadline}>
            Secure authentication, private rooms, and instant WebSocket messaging — built with Spring Boot, React, and MongoDB.
          </p>

          {/* Decorative chat preview */}
          <div className={styles.preview} aria-hidden>
            <div className={styles.previewBar}>
              <div className={styles.previewDot} style={{ background: '#ef4444' }} />
              <div className={styles.previewDot} style={{ background: '#f59e0b' }} />
              <div className={styles.previewDot} style={{ background: '#10b981' }} />
              <span className={styles.previewTitle}># general-room</span>
            </div>
            <div className={styles.previewMessages}>
              <div className={styles.previewMsg}>
                <div className={styles.previewAvatar} style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)' }}>A</div>
                <div className={styles.previewBubble}>Hey everyone! 👋</div>
              </div>
              <div className={styles.previewMsg}>
                <div className={styles.previewAvatar} style={{ background: 'linear-gradient(135deg,#06b6d4,#6366f1)' }}>B</div>
                <div className={styles.previewBubble}>Welcome to PulseChat!</div>
              </div>
              <div className={`${styles.previewMsg} ${styles.previewMsgOwn}`}>
                <div className={styles.previewBubbleOwn}>This is amazing 🚀</div>
                <div className={styles.previewAvatar} style={{ background: 'linear-gradient(135deg,#10b981,#06b6d4)' }}>Y</div>
              </div>
              <div className={styles.previewTyping}>
                <span /><span /><span />
                <em>Alex is typing…</em>
              </div>
            </div>
          </div>
        </div>

        {/* Action / Auth card */}
        <div className={styles.card}>
          {!isAuthenticated ? (
            /* If not logged in, show AuthCard */
            <AuthCard onAuthSuccess={() => setMode(null)} />
          ) : !mode ? (
            /* Logged in: Welcome & Mode selection */
            <div className={styles.modeSelect}>
              {/* Authenticated user profile banner */}
              <div className={styles.userBanner}>
                <Avatar username={user.name} size={42} />
                <div className={styles.userBannerInfo}>
                  <div className={styles.userBannerName}>
                    <span>{user.name}</span>
                    <CheckCircle2 size={15} className={styles.verifiedIcon} title="Verified account" />
                  </div>
                  <div className={styles.userBannerEmail}>{user.email}</div>
                </div>
                <button
                  type="button"
                  className={styles.logoutBtn}
                  onClick={handleLogout}
                  title="Log out"
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>

              <h2 className={styles.cardTitle}>Start chatting</h2>
              <p className={styles.cardSubtitle}>Choose an option to begin</p>

              <div className={styles.modeButtons}>
                <button className={styles.modeBtn} onClick={() => handleModeSwitch('create')}>
                  <div className={styles.modeBtnIcon}>
                    <Plus size={24} />
                  </div>
                  <div>
                    <div className={styles.modeBtnTitle}>Create a Room</div>
                    <div className={styles.modeBtnSub}>Start a new conversation</div>
                  </div>
                  <ArrowRight size={18} className={styles.modeBtnArrow} />
                </button>
                <button className={styles.modeBtn} onClick={() => handleModeSwitch('join')}>
                  <div className={styles.modeBtnIcon} style={{ background: 'linear-gradient(135deg,#06b6d4,#6366f1)' }}>
                    <ArrowRight size={24} />
                  </div>
                  <div>
                    <div className={styles.modeBtnTitle}>Join a Room</div>
                    <div className={styles.modeBtnSub}>Enter an existing room ID</div>
                  </div>
                  <ArrowRight size={18} className={styles.modeBtnArrow} />
                </button>
              </div>
            </div>
          ) : (
            /* Form for room entry */
            <div className={styles.formSection}>
              <div className={styles.formHeader}>
                <button className={styles.backBtn} onClick={() => setMode(null)}>
                  ← Back
                </button>
                <h2 className={styles.cardTitle}>
                  {mode === 'create' ? 'Create a Room' : 'Join a Room'}
                </h2>
              </div>

              <div className={styles.form}>
                {/* Active user display */}
                <div className={styles.activeUserBadge}>
                  <Avatar username={activeUsername} size={28} />
                  <div>
                    <span className={styles.activeUserLabel}>Chatting as: </span>
                    <strong className={styles.activeUserName}>{activeUsername}</strong>
                  </div>
                </div>

                <div className={styles.field}>
                  <label htmlFor={roomId_id} className={styles.label}>Room ID</label>
                  <div className={`${styles.inputWrapper} ${errors.roomId ? styles.inputError : ''}`}>
                    <Hash size={16} className={styles.inputIcon} />
                    <input
                      id={roomId_id}
                      className={styles.input}
                      placeholder={mode === 'create' ? 'my-room-id' : 'Enter room ID to join'}
                      value={roomId}
                      onChange={e => { setRoomId(e.target.value); setErrors(p => ({ ...p, roomId: undefined })) }}
                      maxLength={50}
                      autoComplete="off"
                      spellCheck={false}
                    />
                    {mode === 'create' && (
                      <button
                        type="button"
                        className={styles.generateBtn}
                        onClick={handleGenerate}
                        title="Generate a random Room ID"
                      >
                        <Sparkles size={14} />
                        <span>Generate</span>
                      </button>
                    )}
                  </div>
                  {errors.roomId && <p className={styles.errorMsg}>{errors.roomId}</p>}
                  {!errors.roomId && (
                    <p className={styles.hint}>
                      {mode === 'create'
                        ? 'Share this ID with others so they can join'
                        : 'Ask the room creator for the exact Room ID'}
                    </p>
                  )}
                </div>

                <button
                  className={`${styles.submitBtn} ${loading ? styles.submitBtnLoading : ''}`}
                  onClick={mode === 'create' ? handleCreate : handleJoin}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <RefreshCw size={16} className={styles.spin} />
                      {mode === 'create' ? 'Creating…' : 'Joining…'}
                    </>
                  ) : (
                    <>
                      <MessageSquare size={16} />
                      {mode === 'create' ? 'Create Room & Enter' : 'Join Room'}
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        <p className={styles.footer}>
          PulseChat &mdash; Built with Spring Boot &amp; React &middot; Real-time WebSocket messaging
        </p>
      </main>
    </div>
  )
}
