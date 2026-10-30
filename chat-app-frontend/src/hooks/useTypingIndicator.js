import { useCallback, useRef } from 'react'

/**
 * useTypingIndicator — handles throttled typing events.
 * Sends a typing:true event when the user starts typing,
 * and a typing:false event when they stop (after a delay).
 */
export function useTypingIndicator(sendTyping) {
  const typingTimeoutRef = useRef(null)
  const isTypingRef = useRef(false)

  const handleTypingStart = useCallback(() => {
    if (!isTypingRef.current) {
      isTypingRef.current = true
      sendTyping(true)
    }

    // Reset stop timer on each keystroke
    clearTimeout(typingTimeoutRef.current)
    typingTimeoutRef.current = setTimeout(() => {
      isTypingRef.current = false
      sendTyping(false)
    }, 2000)
  }, [sendTyping])

  const handleTypingStop = useCallback(() => {
    clearTimeout(typingTimeoutRef.current)
    if (isTypingRef.current) {
      isTypingRef.current = false
      sendTyping(false)
    }
  }, [sendTyping])

  return { handleTypingStart, handleTypingStop }
}
