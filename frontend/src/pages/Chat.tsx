import { useState, useEffect, useRef, useCallback, useReducer } from 'react'
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
  speechText?: string
}

const GREETING =
  "Hi — I'm Rami, your LA City planning and permits assistant. Ask me about a permit, an address, a case number, or how a process works. I'll adapt to whether you're a homeowner, developer, or contractor."

const GREETING_SPOKEN =
  "Hi — I'm Rami, your LA City planning and permits assistant. What can I help you with?"

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
  { label: 'Demolition permit', prompt: 'What do I need to pull a demolition permit for an existing house in LA?' },
  { label: 'Electrical permit steps', prompt: 'Walk me through the process of getting an electrical permit for a panel upgrade.' },
  { label: 'Plumbing permit', prompt: 'When do I need a plumbing permit for a residential re-pipe?' },
  { label: 'Fire sprinkler permit', prompt: 'What are the requirements for a fire sprinkler permit in a commercial retrofit?' },
  { label: 'Certificate of Occupancy', prompt: 'How do I get a Certificate of Occupancy for a newly built home in LA?' },
  { label: 'Variance process', prompt: 'My property doesn\'t meet the setback rules — how do I apply for a variance?' },
  { label: 'Sign permit', prompt: 'What permits do I need to install a business sign on my storefront?' },
  { label: 'Short-term rental permit', prompt: 'Do I need a permit to operate a short-term rental like an Airbnb in LA?' },
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
  | { type: 'synthesizing' }
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
    case 'synthesizing':
      return 'synthesizing'
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
    { role: 'assistant', content: GREETING, speechText: GREETING_SPOKEN },
  ])
  const [loading, setLoading] = useState(false)
  const [detectedPersona, setDetectedPersona] = useState<string | null>(null)
  const [serverError, setServerError] = useState<string | null>(null)
  const [hasUserMessage, setHasUserMessage] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [conversationState, dispatchCS] = useReducer(conversationReducer, 'idle')

  const pickSuggestions = useCallback(() => {
    const shuffled = [...SUGGESTIONS].sort(() => Math.random() - 0.5)
    return shuffled.slice(0, 5)
  }, [])

  const [visibleSuggestions, setVisibleSuggestions] = useState<Suggestion[]>(() => pickSuggestions())
  const [spinning, setSpinning] = useState(false)

  const refreshSuggestions = useCallback(() => {
    setSpinning(true)
    setVisibleSuggestions(pickSuggestions())
    setTimeout(() => setSpinning(false), 400)
  }, [pickSuggestions])

  const bottomRef = useRef<HTMLDivElement>(null)
  const messagesRef = useRef<HTMLDivElement>(null)
  const isAtBottomRef = useRef(true)
  const processingRef = useRef(false)

  // ── Speech hooks ──────────────────────────────────────────────────────────────
  const { token, region } = useSpeechToken()
  const { scheduleViseme, currentVisemeId, clearQueue, startPlayback } = useVisemeScheduler()
  const { speak, isSynthesizing, isSpeaking, stop: stopSpeaking, resumeAudio } = useSpeechSynthesizer({
    token,
    region,
    language: 'en-US',
    onViseme: (id, offsetMs) => scheduleViseme(id, offsetMs),
    onSynthesized: (_text, _chunks) => {
      // Saving to IndexedDB is now handled inside useSpeechSynthesizer
    },
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

  const prevSynthesizingRef = useRef(isSynthesizing)
  const prevSpeakingRef = useRef(isSpeaking)
  useEffect(() => {
    if (isSynthesizing && !prevSynthesizingRef.current) {
      dispatchCS({ type: 'synthesizing' })
    } else if (isSpeaking && !prevSpeakingRef.current) {
      dispatchCS({ type: 'speaking' })
    } else if (!isSynthesizing && !isSpeaking && (prevSynthesizingRef.current || prevSpeakingRef.current)) {
      dispatchCS({ type: 'idle' })
    }
    prevSynthesizingRef.current = isSynthesizing
    prevSpeakingRef.current = isSpeaking
  }, [isSynthesizing, isSpeaking])

  // ── Speak greeting on page load ──────────────────────────────────────────────
  const greetingSpokenRef = useRef(false)
  useEffect(() => {
    if (isSpeechReady && !greetingSpokenRef.current) {
      greetingSpokenRef.current = true
      startPlayback()
      speak(GREETING_SPOKEN).catch(() => {})
    }
  }, [isSpeechReady, startPlayback, speak])

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
      setMessages([...next, { role: 'assistant', content: reply, speechText }])

      if (data.detected_persona && !detectedPersona) {
        setDetectedPersona(data.detected_persona)
      }
      setSuggestions(data.suggestions ?? [])

      startPlayback()
      speak(speechText).catch(() => {})
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

    if (isSpeaking || isSynthesizing) {
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
  }, [messages, isSpeaking, isSynthesizing, stopSpeaking, clearQueue, sendToApi])

  // ── Text send handler ─────────────────────────────────────────────────────────
  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || loading) return

    if (isSpeaking || isSynthesizing) {
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
  }, [messages, loading, isSpeaking, isSynthesizing, stopSpeaking, clearQueue, sendToApi])

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

  const handleReplaySpeech = useCallback((text: string) => {
    if (isSpeaking || isSynthesizing) {
      stopSpeaking()
      clearQueue()
    }
    startPlayback()
    void speak(text)
  }, [speak, startPlayback, stopSpeaking, clearQueue, isSpeaking, isSynthesizing])

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

        {/* Main nav */}
        <div className={styles.mainNav}>
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

      <div className={styles.pageBody}>

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
        <div className={`${styles.topArea}${hasUserMessage ? ` ${styles.topAreaCentered}` : ''}`}>
          <ChatMascot visemeId={currentVisemeId} state={conversationState} />
          {!hasUserMessage && (
            <div className={styles.suggestions} aria-label="Suggested prompts">
              <div className={styles.suggestionsHeader}>
                <p className={styles.suggestionsLabel}>Try asking…</p>
                <button
                  type="button"
                  className={styles.refreshBtn}
                  onClick={refreshSuggestions}
                  aria-label="Refresh suggestions"
                  title="Refresh suggestions"
                >
                  <i className={`fa-solid fa-rotate-right ${styles.refreshIcon}${spinning ? ` ${styles.spinning}` : ''}`} aria-hidden="true" />
                </button>
              </div>
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
          isSpeaking={isSpeaking || isSynthesizing}
          onMuteToggle={handleMuteToggle}
          onStopTTS={handleStopTTS}
          onReplaySpeech={handleReplaySpeech}
        />
        <div ref={bottomRef} />
      </main>

      {/* ── lacity.gov-style footer ── */}
      <footer className={styles.siteFooter}>
        <div className={styles.videoBanner} aria-hidden="true">
          <video
            src={`${import.meta.env.VITE_API_URL}/static/lacity-banner.mp4`}
            className={styles.bannerVideo}
            autoPlay
            loop
            muted
            playsInline
          />
        </div>
        <div className={styles.footerInner}>
          <div className={styles.footerTop}>

            {/* Col 1 — City of LA */}
            <div className={styles.footerCol}>
              <h2 className={styles.footerColHeading}>City of Los Angeles</h2>
              <p className={styles.footerText}>
                200 N Spring St.<br />
                Los Angeles, CA 90012<br />
                Call 311 or 213-473-3231<br />
                TDD Service Call 7-1-1
              </p>

            </div>

            {/* Col 2 — Quick Links */}
            <div className={styles.footerCol}>
              <h2 className={styles.footerColHeading}>Quick Links</h2>
              <a href="https://lacity.gov/residents" className={styles.footerLink} target="_blank" rel="noopener noreferrer">Support for Residents</a>
              <a href="https://lacity.gov/business" className={styles.footerLink} target="_blank" rel="noopener noreferrer">Tools for Business</a>
              <a href="https://lacity.gov/visitors" className={styles.footerLink} target="_blank" rel="noopener noreferrer">Tips for Visitors</a>
              <a href="https://lacity.gov/jobs" className={styles.footerLink} target="_blank" rel="noopener noreferrer">Search for Jobs</a>
              <a href="https://lacity.gov/government" className={styles.footerLink} target="_blank" rel="noopener noreferrer">Meet Your Government</a>
            </div>

            {/* Col 3 — Connect With Us */}
            <div className={styles.footerCol}>
              <h2 className={styles.footerColHeading}>Connect With Us</h2>
              <a href="https://x.com/lacity" className={styles.footerSocial} target="_blank" rel="noopener noreferrer">
                <i className="fa-brands fa-x-twitter" aria-hidden="true" /> x.com/LACity
              </a>
              <a href="https://facebook.com/LACity" className={styles.footerSocial} target="_blank" rel="noopener noreferrer">
                <i className="fa-brands fa-facebook-f" aria-hidden="true" /> facebook.com/LACity
              </a>
              <a href="https://instagram.com/LACity" className={styles.footerSocial} target="_blank" rel="noopener noreferrer">
                <i className="fa-brands fa-instagram" aria-hidden="true" /> instagram.com/LACity
              </a>
              <a href="https://www.youtube.com/@LACity" className={styles.footerSocial} target="_blank" rel="noopener noreferrer">
                <i className="fa-brands fa-youtube" aria-hidden="true" /> youtube.com/@LACity
              </a>
            </div>

          </div>

          {/* Bottom bar */}
          <div className={styles.footerBottom}>
            <p className={styles.footerCopy}>© Copyright 2026 City of Los Angeles. All rights reserved.</p>
            <nav className={styles.footerLegal} aria-label="Footer legal links">
              <a href="https://disclaimer.lacity.gov/disclaimer.htm" className={styles.footerLegalLink} target="_blank" rel="noopener noreferrer">Disclaimer</a>
              <a href="https://disclaimer.lacity.gov/privacy.htm" className={styles.footerLegalLink} target="_blank" rel="noopener noreferrer">Privacy Policy</a>
              <a href="https://lacity.gov/public-records-request" className={styles.footerLegalLink} target="_blank" rel="noopener noreferrer">Records Request</a>
              <a href="https://disclaimer.lacity.gov/accessibility.htm" className={styles.footerLegalLink} target="_blank" rel="noopener noreferrer">Accessibility Statement</a>
            </nav>
          </div>
        </div>
      </footer>

      </div>{/* /pageBody */}

    </div>
  )
}
