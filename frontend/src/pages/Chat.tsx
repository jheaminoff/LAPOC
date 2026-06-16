import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ChatWindow from '@/components/ChatWindow'
import styles from './Chat.module.css'

export type Message = {
  role: 'user' | 'assistant'
  content: string
}

const GREETINGS: Record<string, string> = {
  resident: "Hi! I'm your LA City planning assistant. You can ask me about permits for your home, ADUs, remodels, or look up the status of any permit by address or APN. What would you like to know?",
  developer: "Welcome. I can look up entitlement cases, permit status, zoning, and workflow requirements for any LA parcel. Provide an APN, address, or case number to get started.",
  contractor: "Ready to help. Give me a permit number, APN, or address and I'll pull up the current PC status, outstanding fees, and next inspection steps.",
}

const PERSONA_LABELS: Record<string, string> = {
  resident: 'Homeowner / Resident',
  developer: 'Developer',
  contractor: 'Contractor',
}

export default function Chat() {
  const { persona = 'resident' } = useParams<{ persona: string }>()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: GREETINGS[persona] ?? GREETINGS.resident },
  ])
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text: string) => {
    const userMsg: Message = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setLoading(true)

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona, messages: next }),
      })

      if (!res.ok) throw new Error(`Server error ${res.status}`)

      const data = await res.json()
      setMessages([...next, { role: 'assistant', content: data.reply }])
    } catch {
      setMessages([
        ...next,
        { role: 'assistant', content: 'Sorry, I ran into a problem reaching the server. Please try again.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <img
            src="https://www.lacity.gov/sites/default/files/images/2020/city-seal.png"
            alt="City of Los Angeles seal"
            className={styles.seal}
          />
          <button className={styles.back} onClick={() => navigate('/')} aria-label="Back to home">
            ← Back
          </button>
          <div className={styles.titleGroup}>
            <span className={styles.dept}>City of Los Angeles — Planning &amp; Permits</span>
            <h1 className={styles.title}>Planning Assistant</h1>
          </div>
          <span className={styles.badge}>{PERSONA_LABELS[persona]}</span>
        </div>
      </header>

      <main className={styles.main}>
        <ChatWindow messages={messages} loading={loading} onSend={sendMessage} />
        <div ref={bottomRef} />
      </main>
    </div>
  )
}
