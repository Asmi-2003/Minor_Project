import { useState, useId } from 'react'
import { useAuth } from '../context/AuthContext'
import { useToast } from './Toast'
import { Mail, Lock, User, LogIn, UserPlus, RefreshCw, AlertCircle } from 'lucide-react'
import styles from './AuthCard.module.css'

export function AuthCard({ onAuthSuccess }) {
  const { login, signup } = useAuth()
  const { addToast } = useToast()

  const [mode, setMode] = useState('login') // 'login' | 'signup'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const nameId = useId()
  const emailId = useId()
  const passwordId = useId()

  function validate() {
    const errs = {}
    if (mode === 'signup') {
      if (!name.trim()) errs.name = 'Full name is required'
      else if (name.trim().length < 2) errs.name = 'Name must be at least 2 characters'
    }

    if (!email.trim()) {
      errs.email = 'Email address is required'
    } else if (!/^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(email.trim())) {
      errs.email = 'Please enter a valid email address (e.g., user@gmail.com)'
    }

    if (!password) {
      errs.password = 'Password is required'
    } else if (password.length < 6) {
      errs.password = 'Password must be at least 6 characters'
    }

    return errs
  }

  async function handleSubmit(e) {
    e?.preventDefault()
    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setLoading(true)
    try {
      if (mode === 'signup') {
        const user = await signup({
          name: name.trim(),
          email: email.trim().toLowerCase(),
          password,
        })
        addToast(`Welcome to PulseChat, ${user.name}!`, 'success')
      } else {
        const user = await login({
          email: email.trim().toLowerCase(),
          password,
        })
        addToast(`Welcome back, ${user.name}!`, 'success')
      }
      onAuthSuccess?.()
    } catch (err) {
      if (err.status === 409) {
        setErrors(prev => ({ ...prev, email: 'This email is already registered. Please log in.' }))
        addToast('This email is already registered. Please log in.', 'error')
      } else if (err.status === 401) {
        setErrors(prev => ({ ...prev, form: 'Invalid email or password' }))
        addToast('Invalid email or password', 'error')
      } else {
        setErrors(prev => ({ ...prev, form: err.message || 'Authentication failed' }))
        addToast(err.message || 'Authentication failed', 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  function switchMode(newMode) {
    setMode(newMode)
    setErrors({})
  }

  return (
    <div className={styles.container}>
      {/* Tab Switcher */}
      <div className={styles.tabBar}>
        <button
          type="button"
          className={`${styles.tabBtn} ${mode === 'login' ? styles.tabBtnActive : ''}`}
          onClick={() => switchMode('login')}
        >
          <LogIn size={15} />
          <span>Login</span>
        </button>
        <button
          type="button"
          className={`${styles.tabBtn} ${mode === 'signup' ? styles.tabBtnActive : ''}`}
          onClick={() => switchMode('signup')}
        >
          <UserPlus size={15} />
          <span>Sign Up</span>
        </button>
      </div>

      <div className={styles.header}>
        <h2 className={styles.title}>
          {mode === 'login' ? 'Welcome back' : 'Create an account'}
        </h2>
        <p className={styles.subtitle}>
          {mode === 'login'
            ? 'Sign in with your email to start chatting'
            : 'Register with your email to join PulseChat'}
        </p>
      </div>

      {errors.form && (
        <div className={styles.alertError}>
          <AlertCircle size={16} />
          <span>{errors.form}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form} noValidate>
        {mode === 'signup' && (
          <div className={styles.field}>
            <label htmlFor={nameId} className={styles.label}>Your Name</label>
            <div className={`${styles.inputWrapper} ${errors.name ? styles.inputError : ''}`}>
              <User size={16} className={styles.inputIcon} />
              <input
                id={nameId}
                type="text"
                className={styles.input}
                placeholder="Alex Rivers"
                value={name}
                onChange={e => { setName(e.target.value); setErrors(p => ({ ...p, name: undefined })) }}
                maxLength={50}
                autoComplete="name"
              />
            </div>
            {errors.name && <p className={styles.errorText}>{errors.name}</p>}
          </div>
        )}

        <div className={styles.field}>
          <label htmlFor={emailId} className={styles.label}>Email Address</label>
          <div className={`${styles.inputWrapper} ${errors.email ? styles.inputError : ''}`}>
            <Mail size={16} className={styles.inputIcon} />
            <input
              id={emailId}
              type="email"
              className={styles.input}
              placeholder="alex@gmail.com"
              value={email}
              onChange={e => { setEmail(e.target.value); setErrors(p => ({ ...p, email: undefined, form: undefined })) }}
              autoComplete="email"
              spellCheck={false}
            />
          </div>
          {errors.email && <p className={styles.errorText}>{errors.email}</p>}
        </div>

        <div className={styles.field}>
          <label htmlFor={passwordId} className={styles.label}>Password</label>
          <div className={`${styles.inputWrapper} ${errors.password ? styles.inputError : ''}`}>
            <Lock size={16} className={styles.inputIcon} />
            <input
              id={passwordId}
              type="password"
              className={styles.input}
              placeholder={mode === 'signup' ? 'Min. 6 characters' : 'Enter password'}
              value={password}
              onChange={e => { setPassword(e.target.value); setErrors(p => ({ ...p, password: undefined, form: undefined })) }}
              autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
            />
          </div>
          {errors.password && <p className={styles.errorText}>{errors.password}</p>}
        </div>

        <button
          type="submit"
          className={`${styles.submitBtn} ${loading ? styles.submitBtnLoading : ''}`}
          disabled={loading}
        >
          {loading ? (
            <>
              <RefreshCw size={16} className={styles.spin} />
              {mode === 'login' ? 'Signing in…' : 'Creating account…'}
            </>
          ) : (
            <>
              {mode === 'login' ? <LogIn size={16} /> : <UserPlus size={16} />}
              {mode === 'login' ? 'Sign In to PulseChat' : 'Create Free Account'}
            </>
          )}
        </button>
      </form>

      <p className={styles.switchNotice}>
        {mode === 'login' ? (
          <>
            Don't have an account?{' '}
            <button type="button" className={styles.linkBtn} onClick={() => switchMode('signup')}>
              Sign up with Gmail
            </button>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <button type="button" className={styles.linkBtn} onClick={() => switchMode('login')}>
              Log in here
            </button>
          </>
        )}
      </p>
    </div>
  )
}

