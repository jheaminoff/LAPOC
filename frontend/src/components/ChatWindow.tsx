import { useState, useRef, useEffect, type KeyboardEvent } from 'react'
import type { Message } from '@/pages/Chat'
import CaseStatusBadge from './CaseStatusBadge'
import styles from './ChatWindow.module.css'

type Props = {
  messages: Message[]
  loading: boolean
  onSend: (text: string) => void
}

/** Very light Markdown-ish renderer: bold, bullet lists, line breaks */
function renderContent(text: string) {
  return text.split('\n').map((line, i) => {
    // Bold: **text**
    const parts = line.split(/(\*\*[^*]+\*\*)/).map((part, j) =>
      part.startsWith('**') && part.endsWith('**')
        ? <strong key={j}>{part.slice(2, -2)}</strong>
        : part
    )
    // Bullet lines
    const isBullet = line.trimStart().startsWith('•') || line.trimStart().startsWith('-')
    if (isBullet) {
      return <li key={i} className={styles.bullet}>{parts}</li>
    }
    return <p key={i} className={styles.line}>{parts}</p>
  })
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
            <div className={styles.content}>
              <div className={styles.text}>{renderContent(msg.content)}</div>
              <CaseStatusBadge content={msg.content} />
            </div>
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
