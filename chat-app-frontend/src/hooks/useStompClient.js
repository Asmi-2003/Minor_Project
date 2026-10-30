import { useEffect, useRef, useState, useCallback } from 'react'
import { Client } from '@stomp/stompjs'
import SockJS from 'sockjs-client'

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8081/chat'

/**
 * useStompClient — manages STOMP/SockJS WebSocket connection.
 * Handles connect, disconnect, reconnect, subscriptions, and message sending.
 */
export function useStompClient({ roomId, username, onMessage, onTyping, onParticipants, onConnect, onDisconnect }) {
  const clientRef = useRef(null)
  const subscriptionsRef = useRef([])
  const [connected, setConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('disconnected') // 'connecting' | 'connected' | 'disconnected' | 'error'
  const isConnectedRef = useRef(false)

  const cleanupSubscriptions = useCallback(() => {
    subscriptionsRef.current.forEach(sub => {
      try { sub.unsubscribe() } catch {}
    })
    subscriptionsRef.current = []
  }, [])

  const connect = useCallback(() => {
    if (clientRef.current?.active) return

    setConnectionStatus('connecting')

    const client = new Client({
      webSocketFactory: () => new SockJS(WS_URL),
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,

      onConnect: () => {
        isConnectedRef.current = true
        setConnected(true)
        setConnectionStatus('connected')

        // Subscribe to room messages
        const msgSub = client.subscribe(`/topic/room/${roomId}`, (frame) => {
          try {
            const msg = JSON.parse(frame.body)
            onMessage?.(msg)
          } catch {}
        })

        // Subscribe to typing indicators
        const typingSub = client.subscribe(`/topic/room/${roomId}/typing`, (frame) => {
          try {
            const event = JSON.parse(frame.body)
            onTyping?.(event)
          } catch {}
        })

        // Subscribe to participant count updates
        const participantSub = client.subscribe(`/topic/room/${roomId}/participants`, (frame) => {
          try {
            const event = JSON.parse(frame.body)
            onParticipants?.(event)
          } catch {}
        })

        subscriptionsRef.current = [msgSub, typingSub, participantSub]

        // Announce join
        client.publish({
          destination: `/app/join/${roomId}`,
          body: JSON.stringify({ sender: username, roomId }),
        })

        onConnect?.()
      },

      onDisconnect: () => {
        isConnectedRef.current = false
        setConnected(false)
        setConnectionStatus('disconnected')
        cleanupSubscriptions()
        onDisconnect?.()
      },

      onStompError: (frame) => {
        console.error('STOMP error:', frame.headers?.message)
        setConnectionStatus('error')
      },

      onWebSocketError: (event) => {
        console.error('WebSocket error:', event)
        setConnectionStatus('error')
      },
    })

    clientRef.current = client
    client.activate()
  }, [roomId, username, onMessage, onTyping, onParticipants, onConnect, onDisconnect, cleanupSubscriptions])

  const disconnect = useCallback(() => {
    if (clientRef.current?.active) {
      // Announce leave before disconnecting
      try {
        clientRef.current.publish({
          destination: `/app/leave/${roomId}`,
          body: JSON.stringify({ sender: username, roomId }),
        })
      } catch {}
      cleanupSubscriptions()
      clientRef.current.deactivate()
    }
    isConnectedRef.current = false
    setConnected(false)
    setConnectionStatus('disconnected')
  }, [roomId, username, cleanupSubscriptions])

  const sendMessage = useCallback((content) => {
    if (!clientRef.current?.active || !isConnectedRef.current) return false
    try {
      clientRef.current.publish({
        destination: `/app/sendMessage/${roomId}`,
        body: JSON.stringify({ content, sender: username, roomId }),
      })
      return true
    } catch (e) {
      console.error('Send failed:', e)
      return false
    }
  }, [roomId, username])

  const sendTyping = useCallback((isTyping) => {
    if (!clientRef.current?.active || !isConnectedRef.current) return
    try {
      clientRef.current.publish({
        destination: `/app/typing/${roomId}`,
        body: JSON.stringify({ sender: username, roomId, typing: isTyping }),
      })
    } catch {}
  }, [roomId, username])

  useEffect(() => {
    if (roomId && username) {
      connect()
    }
    return () => {
      disconnect()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId, username])

  return { connected, connectionStatus, sendMessage, sendTyping, disconnect }
}
