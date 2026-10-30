import styles from './TypingIndicator.module.css'

export function TypingIndicator({ typingUsers }) {
  if (!typingUsers || typingUsers.length === 0) return null

  let label
  if (typingUsers.length === 1) {
    label = `${typingUsers[0]} is typing`
  } else if (typingUsers.length === 2) {
    label = `${typingUsers[0]} and ${typingUsers[1]} are typing`
  } else {
    label = `${typingUsers.length} people are typing`
  }

  return (
    <div className={styles.wrapper} aria-live="polite">
      <div className={styles.dots}>
        <span /><span /><span />
      </div>
      <span className={styles.label}>{label}&hellip;</span>
    </div>
  )
}
