import { useState, useEffect, useRef, useCallback, useReducer, useMemo } from 'react'
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
  "Hi — I'm Rami, your LA City planning and permits assistant. Ask me about a permit, an address, a case number, or how a process works. I'll adapt to whether you're a homeowner, developer, or contractor."

const PERSONA_LABELS: Record<string, string> = {
  resident: 'Homeowner / Resident',
  developer: 'Developer',
  contractor: 'Contractor',
}

type Suggestion = {
  label: string
  prompt: string
  dynamic?: boolean
}

const SUGGESTIONS: Suggestion[] = [
  { label: 'Look up a permit', prompt: 'I want to look up permit status for 2815 Sunset Blvd, Silver Lake.' },
  { label: 'ADU process steps', prompt: 'What are the steps to add an ADU to my property?' },
  { label: 'Case status', prompt: 'Can you check the status of case ZA-2024-003812-CUB?', dynamic: true },
  { label: 'How long does plan check take?', prompt: 'How long does residential plan check typically take at LADBS?' },
  { label: 'Zone change steps', prompt: 'What is the process for a zone change on a property in LA?' },
  { label: 'Developer: TOC benefits', prompt: 'How does the Transit Oriented Communities program affect my project feasibility?' },
  { label: 'Contractor: pull a permit', prompt: 'I need to pull an electrical permit — what info do I need to bring to the LADBS office?' },
  { label: 'Conditional Use Permit', prompt: 'What\'s required to get a Conditional Use Permit for alcohol sales in LA?' },
  { label: 'Grading permit steps', prompt: 'What permits do I need before starting grading on a hillside lot in LA?' },
  { label: 'New construction process', prompt: 'Walk me through the steps to permit a new single-family home in Los Angeles.' },
  { label: 'Swimming pool permit', prompt: 'What do I need to get a permit for a new swimming pool or spa?' },
  { label: 'Coastal Development Permit', prompt: 'My property is near the coast — do I need a Coastal Development Permit?' },
  { label: 'Resident: ADU cost estimate', prompt: 'How much does it typically cost to permit and build an ADU in Los Angeles?' },
  { label: 'Developer: CEQA thresholds', prompt: 'When does my project trigger a full EIR versus a Mitigated Negative Declaration?' },
  { label: 'Contractor: HVAC permit', prompt: 'What do I need to pull an HVAC permit for a residential replacement system?' },
  { label: 'Tenant improvement permit', prompt: 'How do I get a permit for a commercial tenant improvement build-out?' },
]

interface ChatResponse {
  reply: string
  speech_text?: string
  detected_persona?: string
  suggestions?: string[]
}

interface RandomCaseResponse {
  case_id: string
}

type ConversationAction =
  | { type: 'listening_started' }
  | { type: 'listening_stopped' }
  | { type: 'thinking' }
  | { type: 'speaking' }
  | { type: 'idle' }

function conversationReducer(state: ConversationState, action: ConversationAction): ConversationState {
  switch (action.type) {
    case 'listening_started':
      return state === 'idle' ? 'listening' : state
    case 'listening_stopped':
      return state !== 'idle' && state !== 'thinking' ? 'idle' : state
    case 'thinking':
      return 'thinking'
    case 'speaking':
      return 'speaking'
    case 'idle':
      return 'idle'
  }
}

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
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [conversationState, dispatchCS] = useReducer(conversationReducer, 'idle')

  const visibleSuggestions = useMemo(() => {
    const shuffled = [...SUGGESTIONS].sort(() => Math.random() - 0.5)
    return shuffled.slice(0, 5)
  }, [])

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
    onResult: (text) => { void handleVoiceResult(text) },
  })

  // ── Speech credentials ───────────────────────────────────────────────────────
  const isSpeechReady = !!token && !!region

  // ── Conversation state sync ───────────────────────────────────────────────────
  const prevListeningRef = useRef(isListening)
  useEffect(() => {
    if (isListening && !prevListeningRef.current) {
      dispatchCS({ type: 'listening_started' })
    } else if (!isListening && prevListeningRef.current) {
      dispatchCS({ type: 'listening_stopped' })
    }
    prevListeningRef.current = isListening
  }, [isListening])

  // ── Shared API call logic ─────────────────────────────────────────────────────
  const sendToApi = useCallback(async (next: Message[]) => {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS)
    setLoading(true)
    setServerError(null)
    dispatchCS({ type: 'thinking' })

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona: 'auto', messages: next }),
        signal: controller.signal,
      })

      if (!res.ok) throw new Error(`Server responded with ${res.status}`)

      const data: ChatResponse = await res.json() as ChatResponse
      const reply = data.reply
      const speechText = data.speech_text || reply
      setMessages([...next, { role: 'assistant', content: reply }])

      if (data.detected_persona && !detectedPersona) {
        setDetectedPersona(data.detected_persona)
      }
      setSuggestions(data.suggestions ?? [])

      dispatchCS({ type: 'speaking' })
      startPlayback()
      speak(speechText)
    } catch (err) {
      const isTimeout = err instanceof DOMException && err.name === 'AbortError'
      const msg = isTimeout
        ? 'The request timed out after 30 seconds. The server may be busy — please try again.'
        : 'Sorry, I couldn\'t reach the server. Please check that the backend is running and try again.'
      setServerError(msg)
      dispatchCS({ type: 'idle' })
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
    setSuggestions([])
    const userMsg: Message = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setHasUserMessage(true)
    await sendToApi(next)
  }, [messages, loading, isSpeaking, stopSpeaking, clearQueue, sendToApi])

  // ── Suggestion click handler (supports dynamic suggestions) ──────────────────
  const handleSuggestionClick = useCallback(async (s: Suggestion) => {
    if (s.dynamic) {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/cases/random`)
        if (res.ok) {
          const data: RandomCaseResponse = await res.json() as RandomCaseResponse
          const prompt = `Can you check the status of case ${data.case_id}?`
          await sendMessage(prompt)
          return
        }
      } catch {
        // fall through to static prompt on error
      }
    }
    await sendMessage(s.prompt)
  }, [sendMessage])

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
    dispatchCS({ type: 'idle' })
  }, [stopSpeaking, clearQueue])

  return (
    <div className={styles.page}>
      {/* ── lacity.gov-style header ── */}
      <header className={styles.siteHeader}>

        {/* Top utility bar */}
        <div className={styles.utilityBar}>
          <div className={styles.utilityInner}>
            <span className={styles.officialText}>The Official Website of the City of Los Angeles</span>
            <nav className={styles.utilityLinks} aria-label="Utility navigation">
              <a href="https://lacity.gov/myla311" className={styles.utilityLink} target="_blank" rel="noopener noreferrer">
                <i className="fa-solid fa-gear" aria-hidden="true" /> City Services
              </a>
              <a href="https://lacity.gov/directory" className={styles.utilityLink} target="_blank" rel="noopener noreferrer">
                <i className="fa-solid fa-address-book" aria-hidden="true" /> City Directory
              </a>
            </nav>
          </div>
        </div>

        {/* Main nav with drone video background */}
        <div className={styles.mainNav}>
          {/* Drone video background */}
          <div className={styles.videoBg} aria-hidden="true">
            <iframe
              src="https://player.vimeo.com/video/927683120?h=64d73e9e02&background=1&autoplay=1&loop=1&muted=1&byline=0&title=0&portrait=0"
              className={styles.videoIframe}
              allow="autoplay; fullscreen"
              title=""
            />
            <div className={styles.videoOverlay} />
          </div>

          {/* Nav content */}
          <div className={styles.mainNavInner}>
            {/* Logo */}
            <a href="https://lacity.gov" className={styles.logoLink} target="_blank" rel="noopener noreferrer" aria-label="City of Los Angeles">
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Seal_of_Los_Angeles.svg"
                alt="City of Los Angeles seal"
                className={styles.navSeal}
              />
              <span className={styles.logoText}>
                <span className={styles.logoCity}>City of</span>
                <span className={styles.logoLA}>Los Angeles</span>
              </span>
            </a>

            {/* Nav links */}
            <ul className={styles.navLinks} role="list">
              {['RESIDENTS','BUSINESS','VISITORS','JOBS','GOVERNMENT','TV'].map(label => (
                <li key={label}>
                  <a href={`https://lacity.gov/${label.toLowerCase()}`} className={styles.navLink} target="_blank" rel="noopener noreferrer">{label}</a>
                </li>
              ))}
            </ul>

            {/* Icon actions */}
            <div className={styles.navIcons}>
              <button className={styles.navIcon} aria-label="Translate" title="Translate">
                <i className="fa-solid fa-globe" aria-hidden="true" />
              </button>
              <button className={styles.navIcon} aria-label="Accessibility tools" title="Accessibility Tools">
                <i className="fa-solid fa-universal-access" aria-hidden="true" />
              </button>
              <a href="https://lacity.gov/search" className={styles.navIcon} aria-label="Search" title="Search" target="_blank" rel="noopener noreferrer">
                <i className="fa-solid fa-magnifying-glass" aria-hidden="true" />
              </a>
            </div>
          </div>
        </div>

        {/* App sub-bar */}
        <div className={styles.appBar}>
          <div className={styles.appBarInner}>
            <button className={styles.back} onClick={() => navigate('/')} aria-label="Back to home">
              <i className="fa-solid fa-arrow-left" aria-hidden="true" />
            </button>
            <div className={styles.titleGroup}>
              <span className={styles.dept}>City of Los Angeles — Planning &amp; Permits</span>
              <h1 className={styles.title}>Planning Assistant</h1>
            </div>
            {detectedPersona && (
              <span className={styles.badge}>{PERSONA_LABELS[detectedPersona] ?? detectedPersona}</span>
            )}
          </div>
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
                {visibleSuggestions.map((s) => (
                  <button
                    key={s.label}
                    className={styles.chip}
                    onClick={() => { void handleSuggestionClick(s) }}
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
          suggestions={suggestions}
          onSend={(text: string) => { void sendMessage(text) }}
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
