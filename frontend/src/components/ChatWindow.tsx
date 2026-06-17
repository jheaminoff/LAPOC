import { useState, useRef, useEffect, useMemo, type KeyboardEvent } from 'react'
import type { Message } from '@/pages/Chat'
import CaseStatusBadge from './CaseStatusBadge'
import WorkflowTimeline, { parseWorkflowText } from './WorkflowTimeline'
import ParcelCard, { parseParcelText } from './ParcelCard'
import CaseDetailCard, { parseCaseDetailText } from './CaseDetailCard'
import MapCard, { parseMapText } from './MapCard'
import styles from './ChatWindow.module.css'

type Props = {
  messages: Message[]
  loading: boolean
  suggestions: string[]
  onSend: (text: string) => void
  isSpeechReady?: boolean
  isListening?: boolean
  isMuted?: boolean
  isConnecting?: boolean
  isSpeaking?: boolean
  onMuteToggle?: () => void
  onStopTTS?: () => void
  onReplaySpeech?: (text: string) => void
}

const URL_RE = /(https?:\/\/[^\s)>\],"']+)/g

/**
 * Render inline markdown: **bold** and bare https?:// URLs → clickable links.
 * Splits on URLs first, then applies bold within non-URL segments.
 */
function applyInline(line: string): React.ReactNode[] {
  const urlParts = line.split(URL_RE)
  return urlParts.flatMap((part, i) => {
    if (URL_RE.test(part)) {
      URL_RE.lastIndex = 0 // reset stateful regex after test
      return [
        <a
          key={`url-${i}`}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.link}
        >
          {part}
        </a>,
      ]
    }
    // Apply bold within plain-text segments
    return part.split(/(\*\*[^*]+\*\*)/).map((seg, j) =>
      seg.startsWith('**') && seg.endsWith('**')
        ? <strong key={`b-${i}-${j}`}>{seg.slice(2, -2)}</strong>
        : seg,
    )
  })
}

/**
 * Strip structured sentinel blocks from the text before rendering as markdown.
 * The blocks (PARCEL:, CASE DETAIL:, WORKFLOW:) are rendered as visual cards —
 * we don't also want them in the plain-text bubble.
 */
const SENTINEL_RE = /^(PARCEL:|CASE DETAIL:|WORKFLOW:|MAP:)/

function stripStructuredBlocks(text: string): string {
  const lines = text.split('\n')
  const out: string[] = []
  let inBlock = false

  for (const line of lines) {
    if (SENTINEL_RE.test(line.trim())) {
      inBlock = true
      continue
    }
    // A non-indented, non-empty line after a block starts regular text again
    if (inBlock && line.trim() && !line.startsWith('  ') && !line.startsWith('\t')) {
      inBlock = false
    }
    if (!inBlock) out.push(line)
  }

  return out.join('\n').trim()
}

/** Very light Markdown-ish renderer: bold, numbered items, bullet lists, line breaks */
function renderContent(text: string) {
  const cleaned = stripStructuredBlocks(text)
  return cleaned.split('\n').map((line, i) => {
    const trimmed = line.trimStart()
    const indent = line.length - trimmed.length

    // Numbered list: "1. text" or "1) text"
    const numberedMatch = trimmed.match(/^(\d+)[.)]\s+(.*)$/)
    if (numberedMatch) {
      return (
        <p key={i} className={styles.numbered} style={{ paddingLeft: indent ? `${indent * 0.55}em` : undefined }}>
          <span className={styles.numberedIndex}>{numberedMatch[1]}.</span>
          {applyInline(numberedMatch[2])}
        </p>
      )
    }

    // Bullet lines: "- text", "• text" — strip the marker before rendering
    const bulletMatch = trimmed.match(/^[•-]\s+(.*)$/)
    if (bulletMatch) {
      return (
        <li key={i} className={styles.bullet} style={{ paddingLeft: indent ? `${indent * 0.55}em` : undefined }}>
          {applyInline(bulletMatch[1])}
        </li>
      )
    }

    // Plain line (may still have bold or links)
    if (!trimmed) return <br key={i} />
    return <p key={i} className={styles.line}>{applyInline(line)}</p>
  })
}

/** Memoised parsers — one hook per card type, only run for assistant messages */
function useCardData(content: string) {
  const workflow = useMemo(() => parseWorkflowText(content), [content])
  const parcel = useMemo(() => parseParcelText(content), [content])
  const caseDetail = useMemo(() => parseCaseDetailText(content), [content])
  const mapData = useMemo(() => parseMapText(content), [content])
  return { workflow, parcel, caseDetail, mapData }
}

function AssistantContent({ content, speechText, onReplaySpeech }: {
  content: string
  speechText?: string
  onReplaySpeech?: (text: string) => void
}) {
  const { workflow, parcel, caseDetail, mapData } = useCardData(content)
  return (
    <div className={styles.content}>
      <div className={styles.text}>{renderContent(content)}</div>
      {parcel && <ParcelCard data={parcel} />}
      {caseDetail && <CaseDetailCard data={caseDetail} />}
      {workflow && <WorkflowTimeline data={workflow} />}
      {mapData && <MapCard data={mapData} />}
      {/* Suppress inline status badge when CaseDetailCard is already showing status */}
      {!caseDetail && <CaseStatusBadge content={content} />}
      {speechText && onReplaySpeech && (
        <button
          className={styles.replayBtn}
          onClick={() => onReplaySpeech(speechText)}
          aria-label="Replay voice response"
          title="Replay voice response"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55C7.79 13 6 14.79 6 17s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
          </svg>
        </button>
      )}
    </div>
  )
}

export default function ChatWindow({
  messages,
  loading,
  suggestions,
  onSend,
  isSpeechReady,
  isListening,
  isMuted,
  isConnecting,
  isSpeaking,
  onMuteToggle,
  onStopTTS,
  onReplaySpeech,
}: Props) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!loading && textareaRef.current) textareaRef.current.focus()
  }, [loading])

  const handleSend = () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    onSend(text)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`
  }, [input])

  return (
    <div className={styles.wrapper}>
      <div className={styles.messages}>
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.bubble}${msg.role === 'user' ? ` ${styles.user}` : ''}`}
          >
            {msg.role === 'assistant' && (
              <span className={styles.avatar}>LA</span>
            )}
            {msg.role === 'assistant' ? (
              <AssistantContent content={msg.content} speechText={msg.speechText} onReplaySpeech={onReplaySpeech} />
            ) : (
              <div className={styles.content}>
                <div className={styles.text}>{renderContent(msg.content)}</div>
              </div>
            )}
          </div>
        ))}

        {suggestions.length > 0 && messages.filter(m => m.role === 'user').length > 0 && (
          <div className={styles.suggestions}>
            <p className={styles.suggestionsLabel}>Try asking next…</p>
            <div className={styles.chips}>
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  className={styles.chip}
                  onClick={() => onSend(s)}
                  disabled={loading}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className={styles.bubble}>
            <span className={styles.avatar}>LA</span>
            <div className={styles.content}>
              <div className={styles.typing}>
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Voice-forward input area */}
      <div className={styles.voiceInputArea}>
        <button
          className={`${styles.micBtnLarge} ${
            !isSpeechReady      ? styles.micOffLarge :
            isConnecting        ? styles.micConnectingLarge :
            isSpeaking          ? styles.micSpeakingLarge :
            isListening && !isMuted ? styles.micListeningLarge :
            isMuted             ? styles.micMutedLarge :
            styles.micIdleLarge
          }`}
          onClick={onMuteToggle}
          disabled={!isSpeechReady || isConnecting || loading}
          aria-label={
            !isSpeechReady   ? 'Voice unavailable' :
            isConnecting     ? 'Connecting to microphone' :
            isMuted          ? 'Microphone muted — tap to unmute' :
            isListening      ? 'Listening — tap to mute' :
            isSpeaking       ? 'Assistant is speaking' :
            'Tap to speak'
          }
          aria-pressed={isSpeechReady && isListening && !isMuted}
        >
          {isConnecting ? (
            <span className={styles.micSpinner} />
          ) : (
            <span className={styles.micIconLarge}>
              {!isSpeechReady ? (
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M19 11a7 7 0 0 1-.16 1.45l-1.55-1.55A5 5 0 0 0 17 11h-2a3 3 0 0 1-3 3v-.17L10.17 12H10a3 3 0 0 1-3-3V7.83L4.27 5.1A9.9 9.9 0 0 0 3 11H1a11 11 0 0 1 2.11-6.47L1.39 2.81 2.8 1.4l19.8 19.8-1.41 1.41L19 20.59V19h-7v2H9v-2H5v-2h14v2l.16-.16L19 11zM7 11V9.83L5.16 8A5 5 0 0 0 5 9a5 5 0 0 0 5 5v-1.17l-2.83-2.83H7zm5-9a3 3 0 0 1 3 3v4.17l1.45 1.45A5 5 0 0 0 17 9V8a5 5 0 0 0-5-5z"/>
                </svg>
              ) : isMuted ? (
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V20h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/>
                </svg>
              ) : isSpeaking ? (
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
              )}
            </span>
          )}
          {isSpeechReady && isListening && !isMuted && <span className={styles.micRing} />}
          {isSpeechReady && isSpeaking && <span className={styles.micRingSpeaking} />}
        </button>

        <span className={`${styles.micLabel} ${
          !isSpeechReady      ? styles.micLabelOff :
          isConnecting        ? styles.micLabelConnecting :
          isSpeaking          ? styles.micLabelSpeaking :
          isListening && !isMuted ? styles.micLabelListening :
          isMuted             ? styles.micLabelMuted :
          ''
        }`}>
          {!isSpeechReady      ? 'Voice unavailable' :
           isConnecting        ? 'Connecting…' :
           isSpeaking          ? 'Speaking…' :
           isListening && !isMuted ? 'Listening…' :
           isMuted             ? 'Microphone muted' :
           'Tap to speak'}
        </span>

        {isSpeechReady && isSpeaking && (
          <button className={styles.stopBtn} onClick={onStopTTS} aria-label="Stop speaking">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor" aria-hidden="true">
              <rect width="12" height="12" rx="2"/>
            </svg>
            Stop
          </button>
        )}

        {/* Text input row */}
        <div className={styles.textRow}>
          <textarea
            ref={textareaRef}
            className={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Or type your question…"
            rows={1}
            disabled={loading}
          />
          <button
            className={styles.sendBtn}
            onClick={handleSend}
            disabled={loading || !input.trim()}
            aria-label="Send message"
          >
            ↑
          </button>
        </div>

        {isConnecting && (
          <p className={styles.speechHint}>Connecting to speech service…</p>
        )}
        <p className={styles.hint}>Press Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  )
}
