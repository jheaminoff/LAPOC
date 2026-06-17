import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import ChatWindow from '@/components/ChatWindow'
import ChatMascot from '@/components/ChatMascot'
import { useSpeechToken } from '@/hooks/useSpeechToken'
import { useSpeechRecognizer } from '@/hooks/useSpeechRecognizer'
import { useSpeechSynthesizer } from '@/hooks/useSpeechSynthesizer'
import { useVisemeScheduler } from '@/hooks/useVisemeScheduler'
import type { ConversationState } from '@/types/speech'
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

const SUGGESTIONS = [
  { label: 'Look up a permit', prompt: 'I want to look up permit status for 2815 Sunset Blvd, Silver Lake.' },
  { label: 'ADU process steps', prompt: 'What are the steps to add an ADU to my property?' },
  { label: 'Case status', prompt: 'Can you check the status of case ZA-2024-003812-CUB?' },
  { label: 'How long does plan check take?', prompt: 'How long does residential plan check typically take at LADBS?' },
  { label: 'Zone change steps', prompt: 'What is the process for a zone change on a property in LA?' },
  { label: 'Developer: TOC benefits', prompt: 'How does the Transit Oriented Communities program affect my project feasibility?' },
  { label: 'Contractor: pull a permit', prompt: 'I need to pull an electrical permit — what info do I need to bring to the LADBS office?' },
  { label: 'Conditional Use Permit', prompt: 'What\'s required to get a Conditional Use Permit for alcohol sales in LA?' },
]

const FETCH_TIMEOUT_MS = 30_000

export default function Chat() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: GREETING },
  ])
  const [loading, setLoading] = useState(false)
  const [detectedPersona, setDetectedPersona] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)
  const [hasUserMessage, setHasUserMessage] = useState(false)
  const [conversationState, setConversationState] = useState<ConversationState>('idle')

  const bottomRef = useRef<HTMLDivElement>(null)
  const messagesRef = useRef<HTMLDivElement>(null)
  const isAtBottomRef = useRef(true)
  const processingRef = useRef(false)

  // ── Speech hooks ──────────────────────────────────────────────────────────────
  const { token, region } = useSpeechToken()
  const { scheduleViseme, currentVisemeId, clearQueue, startPlayback } = useVisemeScheduler()
  const { speak, isSpeaking, stop: stopSpeaking, resumeAudio } = useSpeechSynthesizer({
    token,
    region,
    language: 'en-US',
    onViseme: (id, offsetMs) => scheduleViseme(id, offsetMs),
  })
  const {
    isListening,
    isConnecting,
    isMuted,
    startListening,
    mute,
    unmute,
  } = useSpeechRecognizer({
    token,
    region,
    language: 'en-US',
    onResult: (text) => handleVoiceResult(text),
  })

  // ── Speech credentials ───────────────────────────────────────────────────────
  const isSpeechReady = !!token && !!region

  // ── Conversation state sync ───────────────────────────────────────────────────
  useEffect(() => {
    if (isListening && conversationState === 'idle') {
      setConversationState('listening')
    }
  }, [isListening, conversationState])

  useEffect(() => {
    if (!isListening && conversationState !== 'idle' && conversationState !== 'thinking') {
      setConversationState('idle')
    }
  }, [isListening, conversationState])

  // ── Shared API call logic ─────────────────────────────────────────────────────
  const sendToApi = useCallback(async (next: Message[]) => {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS)
    setLoading(true)
    setServerError(null)
    setConversationState('thinking')

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona: 'auto', messages: next }),
        signal: controller.signal,
      })

      if (!res.ok) throw new Error(`Server responded with ${res.status}`)

      const data = await res.json()
      const reply = data.reply
      setMessages([...next, { role: 'assistant', content: reply }])

      if (data.detected_persona && !detectedPersona) {
        setDetectedPersona(data.detected_persona)
      }

      setConversationState('speaking')
      startPlayback()
      speak(reply)
    } catch (err) {
      const isTimeout = err instanceof DOMException && err.name === 'AbortError'
      const msg = isTimeout
        ? 'The request timed out after 30 seconds. The server may be busy — please try again.'
        : 'Sorry, I couldn\'t reach the server. Please check that the backend is running and try again.'
      setServerError(msg)
      setConversationState('listening')
    } finally {
      clearTimeout(timer)
      setLoading(false)
    }
  }, [detectedPersona, startPlayback, speak])

  // ── Voice result handler ──────────────────────────────────────────────────────
  const handleVoiceResult = useCallback(async (text: string) => {
    if (!text.trim()) return

    if (isSpeaking) {
      stopSpeaking()
      clearQueue()
    }

    if (processingRef.current) return
    processingRef.current = true

    const userMsg: Message = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setHasUserMessage(true)
    await sendToApi(next)
    processingRef.current = false
  }, [messages, isSpeaking, stopSpeaking, clearQueue, sendToApi])

  // ── Text send handler ─────────────────────────────────────────────────────────
  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || loading) return

    if (isSpeaking) {
      stopSpeaking()
      clearQueue()
    }

    setServerError(null)
    const userMsg: Message = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setHasUserMessage(true)
    await sendToApi(next)
  }, [messages, loading, isSpeaking, stopSpeaking, clearQueue, sendToApi])

  // ── Scroll management ─────────────────────────────────────────────────────────
  useEffect(() => {
    const el = messagesRef.current
    if (!el) return
    const onScroll = () => {
      const threshold = 80
      isAtBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < threshold
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => el.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (isAtBottomRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // ── Mic controls ──────────────────────────────────────────────────────────────
  const handleMuteToggle = useCallback(() => {
    if (!isListening) {
      startListening()
      resumeAudio()
      return
    }
    if (isMuted) unmute()
    else mute()
  }, [isListening, isMuted, mute, unmute, startListening, resumeAudio])

  const handleStopTTS = useCallback(() => {
    stopSpeaking()
    clearQueue()
    setConversationState('listening')
  }, [stopSpeaking, clearQueue])

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
          <button className={styles.back} onClick={() => navigate('/')} aria-label="Back to home">
            ←
          </button>
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
          <button className={styles.errorDismiss} onClick={() => setServerError(null)} aria-label="Dismiss error">
            ✕
          </button>
        </div>
      )}

      <main className={styles.main}>
        {/* Mascot + suggestions area */}
        <div className={styles.topArea}>
          <ChatMascot visemeId={currentVisemeId} state={conversationState} />
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
        </div>

        <ChatWindow
          messages={messages}
          loading={loading}
          onSend={sendMessage}
          isSpeechReady={isSpeechReady}
          isListening={isListening}
          isMuted={isMuted}
          isConnecting={isConnecting}
          isSpeaking={isSpeaking}
          onMuteToggle={handleMuteToggle}
          onStopTTS={handleStopTTS}
        />
        <div ref={bottomRef} />
      </main>
    </div>
  )
}
