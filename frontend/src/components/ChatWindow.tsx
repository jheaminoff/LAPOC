import { useState, useRef, useEffect, useMemo, type KeyboardEvent } from 'react'
import type { Message } from '@/pages/Chat'
import CaseStatusBadge from './CaseStatusBadge'
import WorkflowTimeline, { parseWorkflowText } from './WorkflowTimeline'
import ParcelCard, { parseParcelText } from './ParcelCard'
import CaseDetailCard, { parseCaseDetailText } from './CaseDetailCard'
import styles from './ChatWindow.module.css'

type Props = {
  messages: Message[]
  loading: boolean
  onSend: (text: string) => void
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

/** Very light Markdown-ish renderer: bold, numbered items, bullet lists, line breaks */
function renderContent(text: string) {
  return text.split('\n').map((line, i) => {
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
    const bulletMatch = trimmed.match(/^[•\-]\s+(.*)$/)
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
  return { workflow, parcel, caseDetail }
}

function AssistantContent({ content }: { content: string }) {
  const { workflow, parcel, caseDetail } = useCardData(content)
  return (
    <div className={styles.content}>
      <div className={styles.text}>{renderContent(content)}</div>
      {parcel && <ParcelCard data={parcel} />}
      {caseDetail && <CaseDetailCard data={caseDetail} />}
      {workflow && <WorkflowTimeline data={workflow} />}
      <CaseStatusBadge content={content} />
    </div>
  )
}

export default function ChatWindow({ messages, loading, onSend }: Props) {
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
            className={`${styles.bubble} ${msg.role === 'user' ? styles.user : styles.assistant}`}
          >
            {msg.role === 'assistant' && (
              <span className={styles.avatar}>LA</span>
            )}
            {msg.role === 'assistant' ? (
              <AssistantContent content={msg.content} />
            ) : (
              <div className={styles.content}>
                <div className={styles.text}>{renderContent(msg.content)}</div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className={`${styles.bubble} ${styles.assistant}`}>
            <span className={styles.avatar}>LA</span>
            <div className={styles.content}>
              <div className={styles.typing}>
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className={styles.inputRow}>
        <textarea
          ref={textareaRef}
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about a permit, address, or planning case…"
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
      <p className={styles.hint}>Press Enter to send · Shift+Enter for new line</p>
    </div>
  )
}
