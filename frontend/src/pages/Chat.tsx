import { useState, useEffect, useRef, useCallback } from 'react'
import ChatWindow from '@/components/ChatWindow'
import styles from './Chat.module.css'

export type Message = {
  role: 'user' | 'assistant'
  content: string
}

const GREETING =
  "Hi — I'm your LA City planning and permits assistant. Ask me about a permit, an address, a case number, or how a process works. I'll adapt to whether you're a homeowner, developer, or contractor."

const PERSONA_LABELS: Record<string, string> = {
  resident: 'Homeowner / Resident',
  developer: 'Developer',
  contractor: 'Contractor',
}

/** Prompt suggestion chips shown before the first user message */
const SUGGESTIONS = [
  { label: 'Look up a permit', prompt: 'I want to look up permit status for 2815 Sunset Blvd, Silver Lake.' },
  { label: 'ADU process steps', prompt: 'What are the steps to add an ADU to my property?' },
  { label: 'Case status', prompt: 'Can you check the status of case ZA-2024-003812-CUB?' },
  { label: 'How long does plan check take?', prompt: 'How long does residential plan check typically take at LADBS?' },
]

const FETCH_TIMEOUT_MS = 30_000

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: GREETING },
  ])
  const [loading, setLoading] = useState(false)
  const [detectedPersona, setDetectedPersona] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)
  const [hasUserMessage, setHasUserMessage] = useState(false)

  const bottomRef = useRef<HTMLDivElement>(null)
  const messagesRef = useRef<HTMLDivElement>(null)
  // Track whether user is at/near the bottom so we don't force-scroll while they read
  const isAtBottomRef = useRef(true)

  // Update isAtBottomRef on scroll
  useEffect(() => {
    const el = messagesRef.current
    if (!el) return
    const onScroll = () => {
      const threshold = 80 // px from bottom considered "at bottom"
      isAtBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < threshold
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => el.removeEventListener('scroll', onScroll)
  }, [])

  // Scroll to bottom when messages change — only if user is at (or near) bottom
  useEffect(() => {
    if (isAtBottomRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Always scroll on new user message (they just sent it — keep them at bottom)
  const scrollToBottom = useCallback(() => {
    isAtBottomRef.current = true
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  const sendMessage = useCallback(async (text: string) => {
    setServerError(null)
    const userMsg: Message = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setHasUserMessage(true)
    setLoading(true)
    scrollToBottom()

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS)

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona: 'auto', messages: next }),
        signal: controller.signal,
      })

      if (!res.ok) throw new Error(`Server responded with ${res.status}`)

      const data = await res.json()
      setMessages([...next, { role: 'assistant', content: data.reply }])

      if (data.detected_persona && !detectedPersona) {
        setDetectedPersona(data.detected_persona)
      }
    } catch (err) {
      const isTimeout = err instanceof DOMException && err.name === 'AbortError'
      const msg = isTimeout
        ? 'The request timed out after 30 seconds. The server may be busy — please try again.'
        : 'Sorry, I couldn\'t reach the server. Please check that the backend is running and try again.'
      setServerError(msg)
      // Remove the user's message from history so they can resend
      setMessages(messages)
      setHasUserMessage(messages.length > 1)
    } finally {
      clearTimeout(timer)
      setLoading(false)
    }
  }, [messages, detectedPersona, scrollToBottom])

  return (
    <div className={styles.page}>
      {/* Sticky header */}
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Seal_of_Los_Angeles.svg"
            alt="City of Los Angeles seal"
            className={styles.seal}
          />
          <div className={styles.titleGroup}>
            <span className={styles.dept}>City of Los Angeles — Planning &amp; Permits</span>
            <h1 className={styles.title}>Planning Assistant</h1>
          </div>
          {detectedPersona && (
            <span className={styles.badge}>{PERSONA_LABELS[detectedPersona] ?? detectedPersona}</span>
          )}
        </div>
      </header>

      {/* Error banner */}
      {serverError && (
        <div className={styles.errorBanner} role="alert">
          <span className={styles.errorIcon}>⚠</span>
          <span className={styles.errorText}>{serverError}</span>
          <button
            className={styles.errorDismiss}
            onClick={() => setServerError(null)}
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}

      <main className={styles.main} ref={messagesRef}>
        {/* Empty-state prompt suggestions */}
        {!hasUserMessage && (
          <div className={styles.suggestions} aria-label="Suggested prompts">
            <p className={styles.suggestionsLabel}>Try asking…</p>
            <div className={styles.chips}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s.label}
                  className={styles.chip}
                  onClick={() => sendMessage(s.prompt)}
                  disabled={loading}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        )}

        <ChatWindow messages={messages} loading={loading} onSend={sendMessage} />
        <div ref={bottomRef} />
      </main>
    </div>
  )
}
