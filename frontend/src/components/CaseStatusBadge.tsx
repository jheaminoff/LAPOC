import styles from './CaseStatusBadge.module.css'

type Props = {
  content: string
}

/** Status → colour mapping */
const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  'Permit Finaled':     { bg: '#089e00', text: '#fff' },
  'CofO Issued':        { bg: '#089e00', text: '#fff' },
  'TCO Issued':         { bg: '#3cb371', text: '#fff' },
  'Issued':             { bg: '#000db5', text: '#fff' },
  'PC Approved':        { bg: '#000db5', text: '#fff' },
  'Ready to Issue':     { bg: '#000db5', text: '#fff' },
  'LOD Issued':         { bg: '#000db5', text: '#fff' },
  'Hearing Scheduled':  { bg: '#f5a623', text: '#fff' },
  'Pending Hearing':    { bg: '#f5a623', text: '#fff' },
  'Appeal Pending':     { bg: '#f5a623', text: '#fff' },
  'Corrections Needed': { bg: '#e07b00', text: '#fff' },
  'PC on Hold':         { bg: '#e07b00', text: '#fff' },
  'Fees Due':           { bg: '#cc0000', text: '#fff' },
  'Intent to Revoke':   { bg: '#cc0000', text: '#fff' },
  'Permit Revoked':     { bg: '#cc0000', text: '#fff' },
  'Application Withdrawn': { bg: '#888', text: '#fff' },
  'Under Review':       { bg: '#7b5ea7', text: '#fff' },
  'Completeness Review': { bg: '#7b5ea7', text: '#fff' },
  'Technical Review':   { bg: '#7b5ea7', text: '#fff' },
  'PC Assigned':        { bg: '#555e91', text: '#fff' },
  'Submitted':          { bg: '#555e91', text: '#fff' },
  'CofO in Progress':   { bg: '#2e7d9e', text: '#fff' },
}

/** Scan message text for known status strings and render badges */
export default function CaseStatusBadge({ content }: Props) {
  const found: Array<{ status: string; colors: { bg: string; text: string } }> = []

  for (const [status, colors] of Object.entries(STATUS_COLORS)) {
    if (content.includes(status) && !found.find((f) => f.status === status)) {
      found.push({ status, colors })
    }
  }

  if (found.length === 0) return null

  return (
    <div className={styles.row}>
      {found.map(({ status, colors }) => (
        <span
          key={status}
          className={styles.badge}
          style={{ background: colors.bg, color: colors.text }}
        >
          {status}
        </span>
      ))}
    </div>
  )
}
