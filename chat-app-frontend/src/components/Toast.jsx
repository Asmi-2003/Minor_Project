import { createContext, useContext, useState, useCallback, useRef } from 'react'

const ToastContext = createContext(null)

let toastId = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timersRef = useRef({})

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t))
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
      delete timersRef.current[id]
    }, 350)
  }, [])

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = ++toastId
    setToasts(prev => [...prev.slice(-4), { id, message, type, exiting: false }])

    if (duration > 0) {
      timersRef.current[id] = setTimeout(() => removeToast(id), duration)
    }
    return id
  }, [removeToast])

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="toast-container" aria-live="polite">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            toast={toast}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

function Toast({ toast, onClose }) {
  const icons = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
    warning: '⚠',
  }

  return (
    <div
      className={`toast toast--${toast.type} ${toast.exiting ? 'toast--exiting' : ''}`}
      role="alert"
    >
      <span className="toast__icon">{icons[toast.type] || icons.info}</span>
      <span className="toast__message">{toast.message}</span>
      <button className="toast__close" onClick={onClose} aria-label="Close">✕</button>
    </div>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

/* ---- Inline styles for Toast (to keep them self-contained) ---- */
const toastStyles = `
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 360px;
  width: calc(100vw - 48px);
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 10px;
  backdrop-filter: blur(12px);
  border: 1px solid;
  animation: toastIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  font-size: 0.85rem;
  line-height: 1.4;
}

.toast--exiting {
  animation: toastOut 0.35s ease forwards;
}

.toast--success {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
}

.toast--error {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.toast--info {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
  color: #a5b4fc;
}

.toast--warning {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.4);
  color: #fcd34d;
}

.toast__icon {
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.toast__message {
  flex: 1;
}

.toast__close {
  background: none;
  border: none;
  color: currentColor;
  opacity: 0.6;
  font-size: 0.75rem;
  cursor: pointer;
  flex-shrink: 0;
  padding: 2px;
  line-height: 1;
  transition: opacity 0.15s;
}

.toast__close:hover {
  opacity: 1;
}
`

// Inject toast styles into document head
if (typeof document !== 'undefined') {
  const styleEl = document.createElement('style')
  styleEl.textContent = toastStyles
  document.head.appendChild(styleEl)
}
