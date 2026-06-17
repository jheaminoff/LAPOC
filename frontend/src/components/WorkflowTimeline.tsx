import { useState } from 'react'
import styles from './WorkflowTimeline.module.css'

// -------------------------------------------------------------------------- //
// Types
// -------------------------------------------------------------------------- //

type WorkflowStep = {
  order: number
  name: string
  responsibleParty: string | null
  typicalDays: number | null
  description: string | null
  guidance: string | null
}

type WorkflowData = {
  processType: string
  persona: string
  steps: WorkflowStep[]
}

type Props = {
  data: WorkflowData
}

// -------------------------------------------------------------------------- //
// Parser — converts raw `get_workflow` tool output text into WorkflowData
// -------------------------------------------------------------------------- //

const WORKFLOW_HEADER_RE = /^WORKFLOW:\s*(.+?)\s*\(view:\s*(.+?)\)/m
const STEP_RE = /^\s{2}Step\s+(\d+)\.\s+(.+?)(?:\s+\[(.+?)\])?(?:\s+~(\d+)\s+days)?$/

/**
 * Parse the plain-text output of get_workflow() into a WorkflowData object.
 * Returns null if the text doesn't look like a workflow block.
 */
export function parseWorkflowText(text: string): WorkflowData | null {
  if (!text.includes('WORKFLOW:')) return null

  const headerMatch = text.match(WORKFLOW_HEADER_RE)
  if (!headerMatch) return null

  const processType = headerMatch[1].trim()
  const persona = headerMatch[2].trim()
  const steps: WorkflowStep[] = []

  const lines = text.split('\n')
  let current: WorkflowStep | null = null

  for (const line of lines) {
    const stepMatch = line.match(STEP_RE)
    if (stepMatch) {
      if (current) steps.push(current)
      current = {
        order: parseInt(stepMatch[1], 10),
        name: stepMatch[2].trim(),
        responsibleParty: stepMatch[3]?.trim() ?? null,
        typicalDays: stepMatch[4] ? parseInt(stepMatch[4], 10) : null,
        description: null,
        guidance: null,
      }
      continue
    }

    if (!current) continue

    const trimmed = line.trim()
    if (!trimmed) continue

    // Guidance line starts with 💡
    if (trimmed.startsWith('💡')) {
      current.guidance = trimmed.slice(2).trim()
    } else if (!current.description) {
      current.description = trimmed
    }
  }

  if (current) steps.push(current)
  if (steps.length === 0) return null

  return { processType, persona, steps }
}

// -------------------------------------------------------------------------- //
// Party colour mapping
// -------------------------------------------------------------------------- //

const PARTY_COLORS: Record<string, string> = {
  Applicant: '#e07b00',
  LADBS: '#1c2253',
  'City Planning': '#7b5ea7',
  Applicant_LADBS: '#555e91',
}

function partyColor(party: string | null): string {
  if (!party) return '#888'
  return PARTY_COLORS[party] ?? '#555e91'
}

// -------------------------------------------------------------------------- //
// Step row sub-component
// -------------------------------------------------------------------------- //

const COLLAPSE_THRESHOLD = 7
const INITIAL_VISIBLE = 5

type StepRowProps = {
  step: WorkflowStep
  index: number
  isLast: boolean
}

function StepRow({ step, index, isLast }: StepRowProps) {
  const color = partyColor(step.responsibleParty)

  return (
    <li
      className={styles.step}
      style={{ '--step-delay': `${index * 50}ms` } as React.CSSProperties}
    >
      {/* Left rail */}
      <div className={styles.rail}>
        <div className={styles.circle} style={{ background: color }}>
          {step.order}
        </div>
        {!isLast && <div className={styles.connector} />}
      </div>

      {/* Content */}
      <div className={styles.stepBody}>
        <div className={styles.stepHeader}>
          <span className={styles.stepName}>{step.name}</span>
          <div className={styles.stepMeta}>
            {step.responsibleParty && (
              <span
                className={styles.partyTag}
                style={{ background: color + '18', color }}
              >
                {step.responsibleParty}
              </span>
            )}
            {step.typicalDays && (
              <span className={styles.daysTag}>~{step.typicalDays}d</span>
            )}
          </div>
        </div>
        {step.description && (
          <p className={styles.stepDesc}>{step.description}</p>
        )}
        {step.guidance && (
          <p className={styles.guidance}>
            <span className={styles.guidanceIcon}>💡</span>
            {step.guidance}
          </p>
        )}
      </div>
    </li>
  )
}

// -------------------------------------------------------------------------- //
// Main component
// -------------------------------------------------------------------------- //

export default function WorkflowTimeline({ data }: Props) {
  const [expanded, setExpanded] = useState(false)

  const needsCollapse = data.steps.length > COLLAPSE_THRESHOLD
  const visibleSteps =
    needsCollapse && !expanded ? data.steps.slice(0, INITIAL_VISIBLE) : data.steps
  const hiddenCount = data.steps.length - INITIAL_VISIBLE

  return (
    <div className={styles.card}>
      {/* Header */}
      <div className={styles.cardHeader}>
        <div className={styles.headerLeft}>
          <span className={styles.label}>Workflow</span>
          <span className={styles.processType}>{data.processType}</span>
        </div>
        <span className={styles.stepCount}>{data.steps.length} steps</span>
      </div>

      {/* Timeline */}
      <ol className={styles.timeline} aria-label={`${data.processType} workflow steps`}>
        {visibleSteps.map((step, i) => (
          <StepRow
            key={step.order}
            step={step}
            index={i}
            isLast={i === visibleSteps.length - 1 && (!needsCollapse || expanded)}
          />
        ))}
      </ol>

      {/* Expand / collapse toggle */}
      {needsCollapse && (
        <button
          className={styles.toggle}
          onClick={() => setExpanded((v) => !v)}
          aria-expanded={expanded}
        >
          {expanded ? '▲ Show fewer steps' : `▼ Show all ${hiddenCount + INITIAL_VISIBLE} steps`}
        </button>
      )}
    </div>
  )
}
