import styles from './MessageBubble.module.css'
import { Avatar } from './Avatar'

/**
 * Format a LocalDateTime string (from Java backend) into local time HH:MM.
 */
function formatTime(timeStr) {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    if (isNaN(date.getTime())) return ''
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

export function MessageBubble({ message, isOwn }) {
  const { sender, content, time } = message

  return (
    <div className={`${styles.wrapper} ${isOwn ? styles.own : styles.other}`}>
      {!isOwn && (
        <div className={styles.avatarWrapper}>
          <Avatar username={sender} size={32} />
        </div>
      )}
      <div className={styles.contentWrapper}>
        {!isOwn && (
          <span className={styles.sender}>{sender}</span>
        )}
        <div className={`${styles.bubble} ${isOwn ? styles.bubbleOwn : styles.bubbleOther}`}>
          <p className={styles.text}>{content}</p>
          <span className={styles.time}>{formatTime(time)}</span>
        </div>
      </div>
      {isOwn && (
        <div className={styles.avatarWrapper}>
          <Avatar username={sender} size={32} />
        </div>
      )}
    </div>
  )
}
