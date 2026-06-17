/**
 * CaseDetailCard — parses CASE DETAIL: tool output text and renders a structured case card.
 *
 * Expected input format (from agent/tools.py get_case_detail):
 *   CASE DETAIL: {case_id}
 *     Department:    {dept}
 *     Type:          {process_type}
 *     Description:   {description}
 *     Applicant:     {name} ({type})
 *     Submitted:     {date}
 *     Status:        {status}
 *     Assigned to:   {name}
 *     Fees paid:     ${n}
 *     Fees owed:     ${n}
 *     Hearing date:  {date}   (optional)
 *     Next action:   {text}
 *     Portal link:   {url}    (optional)
 */

import styles from './CaseDetailCard.module.css'

// ─── Types ────────────────────────────────────────────────────────────────────

interface CaseDetailData {
  caseId: string
  department: string
  processType: string
  description: string
  applicant: string
  submitted: string
  status: string
  assignedTo: string
  feesPaid: number
  feesOwed: number
  hearingDate: string | null
  nextAction: string
  portalUrl: string | null
}

// ─── Parser ───────────────────────────────────────────────────────────────────

/**
 * Parse raw CASE DETAIL: tool text into a CaseDetailData object.
 * Returns null if the text doesn't contain a CASE DETAIL: block.
 */
export function parseCaseDetailText(text: string): CaseDetailData | null {
  if (!text.includes('CASE DETAIL:')) return null

  const lines = text.split('\n')
  const headerIdx = lines.findIndex(l => l.startsWith('CASE DETAIL:'))
  if (headerIdx === -1) return null

  const caseId = lines[headerIdx].replace('CASE DETAIL:', '').trim()

  const extract = (label: string): string => {
    const line = lines.find(l => l.trimStart().startsWith(label))
    return line ? line.slice(line.indexOf(label) + label.length).trim() : ''
  }

  const parseFee = (raw: string): number => {
    const m = raw.match(/\$?([\d,]+)/)
    return m ? parseFloat(m[1].replace(/,/g, '')) : 0
  }

  const portalRaw = extract('Portal link:')
  const hearingRaw = extract('Hearing date:')

  return {
    caseId,
    department: extract('Department:'),
    processType: extract('Type:'),
    description: extract('Description:'),
    applicant: extract('Applicant:'),
    submitted: extract('Submitted:'),
    status: extract('Status:'),
    assignedTo: extract('Assigned to:'),
    feesPaid: parseFee(extract('Fees paid:')),
    feesOwed: parseFee(extract('Fees owed:')),
    hearingDate: hearingRaw || null,
    nextAction: extract('Next action:'),
    portalUrl: portalRaw || null,
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<string, { colour: string; bg: string }> = {
  'Permit Finaled':     { colour: '#089e00', bg: '#e8f8e8' },
  'CofO Issued':        { colour: '#089e00', bg: '#e8f8e8' },
  Issued:               { colour: '#089e00', bg: '#e8f8e8' },
  'Ready to Issue':     { colour: '#2e7d32', bg: '#e8f8e8' },
  'PC Approved':        { colour: '#2e7d32', bg: '#e8f8e8' },
  Submitted:            { colour: '#1565c0', bg: '#e3f0fc' },
  'PC Assigned':        { colour: '#1565c0', bg: '#e3f0fc' },
  Recheck:              { colour: '#e07b00', bg: '#fff3e0' },
  'Corrections Needed': { colour: '#e07b00', bg: '#fff3e0' },
  'PC on Hold':         { colour: '#e07b00', bg: '#fff3e0' },
  'Fees Due':           { colour: '#e07b00', bg: '#fff3e0' },
  'Intent to Revoke':   { colour: '#c62828', bg: '#fdecea' },
  'Permit Revoked':     { colour: '#c62828', bg: '#fdecea' },
  'PC Expired':         { colour: '#c62828', bg: '#fdecea' },
  'Application Withdrawn': { colour: '#777', bg: '#f5f5f5' },
}

function getStatusStyle(status: string) {
  return STATUS_CONFIG[status] ?? { colour: '#555', bg: '#f0f0f0' }
}

const DEPT_COLOURS: Record<string, string> = {
  LADBS: '#1c2253',
  'City Planning': '#7b5ea7',
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function StatusBanner({ status, department }: { status: string; department: string }) {
  const { colour, bg } = getStatusStyle(status)
  const deptColour = DEPT_COLOURS[department] ?? '#444'

  return (
    <div className={styles.statusBanner} style={{ background: bg, borderColor: colour }}>
      <span className={styles.statusDot} style={{ background: colour }} aria-hidden="true" />
      <span className={styles.statusText} style={{ color: colour }}>{status}</span>
      <span className={styles.deptTag} style={{ background: deptColour }}>{department}</span>
    </div>
  )
}

function FeeRow({ paid, owed }: { paid: number; owed: number }) {
  const hasOwed = owed > 0
  return (
    <div className={styles.feeRow}>
      <div className={styles.feeItem}>
        <span className={styles.feeLabel}>Fees Paid</span>
        <span className={styles.feePaid}>${paid.toLocaleString()}</span>
      </div>
      <div className={styles.feeDivider} />
      <div className={styles.feeItem}>
        <span className={styles.feeLabel}>Fees Owed</span>
        <span className={hasOwed ? styles.feeOwed : styles.feePaid}>
          {hasOwed ? `⚠ $${owed.toLocaleString()}` : '$0'}
        </span>
      </div>
    </div>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

interface Props {
  data: CaseDetailData
}

export default function CaseDetailCard({ data }: Props) {
  return (
    <div className={styles.card}>
      {/* Header */}
      <div className={styles.cardHeader}>
        <div className={styles.headerTop}>
          <span className={styles.caseId}>{data.caseId}</span>
          <span className={styles.processType}>{data.processType}</span>
        </div>
        {data.description && (
          <p className={styles.description}>{data.description}</p>
        )}
      </div>

      {/* Status banner */}
      <StatusBanner status={data.status} department={data.department} />

      {/* Fee row */}
      <FeeRow paid={data.feesPaid} owed={data.feesOwed} />

      {/* Detail grid */}
      <dl className={styles.detailGrid}>
        {data.submitted && (
          <div className={styles.detailItem}>
            <dt>Submitted</dt>
            <dd>{data.submitted}</dd>
          </div>
        )}
        {data.applicant && (
          <div className={styles.detailItem}>
            <dt>Applicant</dt>
            <dd>{data.applicant}</dd>
          </div>
        )}
        {data.assignedTo && data.assignedTo !== 'Not yet assigned' && (
          <div className={styles.detailItem}>
            <dt>Assigned To</dt>
            <dd>{data.assignedTo}</dd>
          </div>
        )}
        {data.hearingDate && (
          <div className={`${styles.detailItem} ${styles.hearingItem}`}>
            <dt>📅 Hearing Date</dt>
            <dd className={styles.hearingDate}>{data.hearingDate}</dd>
          </div>
        )}
      </dl>

      {/* Next action */}
      {data.nextAction && data.nextAction !== 'None on record' && (
        <div className={styles.nextAction}>
          <span className={styles.nextActionLabel}>Next Action</span>
          <span className={styles.nextActionText}>{data.nextAction}</span>
        </div>
      )}

      {/* Portal link */}
      {data.portalUrl && (
        <div className={styles.portalRow}>
          <a
            href={data.portalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.portalBtn}
          >
            View on Portal ↗
          </a>
        </div>
      )}
    </div>
  )
}
