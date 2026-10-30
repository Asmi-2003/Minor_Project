import styles from './Avatar.module.css'

// Deterministic color palette based on username
const AVATAR_COLORS = [
  ['#6366f1', '#8b5cf6'],
  ['#06b6d4', '#6366f1'],
  ['#10b981', '#06b6d4'],
  ['#f59e0b', '#ef4444'],
  ['#ec4899', '#8b5cf6'],
  ['#8b5cf6', '#ec4899'],
  ['#14b8a6', '#6366f1'],
  ['#f97316', '#ec4899'],
]

function getColorForUsername(username) {
  if (!username) return AVATAR_COLORS[0]
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length]
}

export function Avatar({ username, size = 36 }) {
  const initials = (username || '?')
    .split(/\s+/)
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  const [from, to] = getColorForUsername(username)

  return (
    <div
      className={styles.avatar}
      style={{
        width: size,
        height: size,
        fontSize: size * 0.38,
        background: `linear-gradient(135deg, ${from}, ${to})`,
        flexShrink: 0,
      }}
      aria-label={username}
    >
      {initials}
    </div>
  )
}
