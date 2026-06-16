import { useNavigate } from 'react-router-dom'
import PersonSelector from '@/components/PersonSelector'
import styles from './Landing.module.css'

const personas = [
  {
    id: 'resident',
    label: 'Homeowner / Resident',
    icon: '🏠',
    description: 'Adding a room, building an ADU, remodeling your home, or understanding your property\'s permits.',
  },
  {
    id: 'developer',
    label: 'Developer',
    icon: '🏗️',
    description: 'Entitlements, zone changes, CEQA, tract maps, CUPs, and new construction projects.',
  },
  {
    id: 'contractor',
    label: 'Contractor',
    icon: '🔧',
    description: 'Plan check status, inspections, permit issuance, CofO, and LADBS branch questions.',
  },
] as const

export type Persona = typeof personas[number]['id']

export default function Landing() {
  const navigate = useNavigate()

  const handleSelect = (persona: string) => {
    navigate(`/chat/${persona}`)
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Seal_of_Los_Angeles.svg"
            alt="City of Los Angeles seal"
            className={styles.seal}
          />
          <div>
            <p className={styles.dept}>City of Los Angeles</p>
            <h1 className={styles.title}>Planning &amp; Permits</h1>
          </div>
        </div>
      </header>

      <main className={styles.main}>
        <div className={styles.intro}>
          <h2>How can we help you today?</h2>
          <p>
            Get instant answers about permits, planning cases, and zoning for any
            property in Los Angeles. Choose who you are to get started.
          </p>
        </div>

        <div className={styles.cards}>
          {personas.map((p) => (
            <PersonSelector
              key={p.id}
              icon={p.icon}
              label={p.label}
              description={p.description}
              onClick={() => handleSelect(p.id)}
            />
          ))}
        </div>
      </main>

      <footer className={styles.footer}>
        <p>© 2026 Tampere X LA POC<a href="https://ladbs.org" target="_blank" rel="noreferrer">ladbs.org</a> or <a href="https://planning.lacity.gov" target="_blank" rel="noreferrer">planning.lacity.gov</a></p>
      </footer>
    </div>
  )
}
