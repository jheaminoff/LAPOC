/**
 * ParcelCard — parses PARCEL: tool output text and renders a structured property card.
 *
 * Expected input format (from agent/tools.py lookup_parcel):
 *   PARCEL: {address}
 *     APN: {apn}
 *     Neighborhood: {neighborhood}
 *     Zoning: {zoning}
 *     Lot size: {n} sq ft
 *     Current use: {use}
 *
 *   CASES ({n} total):
 *     [LADBS] {case_id}  |  {process_type}  |  Status: {status}
 *     [City Planning] {case_id}  |  {process_type}  |  Status: {status} | ⚠ ${n} outstanding
 */

import styles from './ParcelCard.module.css'

// ─── Types ────────────────────────────────────────────────────────────────────

interface CaseRow {
  department: string
  caseId: string
  processType: string
  status: string
  feesOutstanding: number | null
}

interface ParcelData {
  address: string
  apn: string
  neighborhood: string
  zoning: string
  lotSize: string | null
  currentUse: string
  cases: CaseRow[]
}

// ─── Parser ───────────────────────────────────────────────────────────────────

/**
 * Parse raw PARCEL: tool text into a ParcelData object.
 * Returns null if the text doesn't contain a PARCEL: block.
 */
export function parseParcelText(text: string): ParcelData | null {
  if (!text.includes('PARCEL:')) return null

  const lines = text.split('\n')
  const parcelLineIdx = lines.findIndex(l => l.startsWith('PARCEL:'))
  if (parcelLineIdx === -1) return null

  const address = lines[parcelLineIdx].replace('PARCEL:', '').trim()

  const extract = (label: string): string => {
    const line = lines.find(l => l.trimStart().startsWith(label))
    return line ? line.replace(label, '').trim() : ''
  }

  const apn = extract('APN:')
  const neighborhood = extract('Neighborhood:')
  const zoning = extract('Zoning:')
  const lotSizeLine = extract('Lot size:')
  const lotSize = lotSizeLine || null
  const currentUse = extract('Current use:')

  // Parse case rows — lines matching "  [DEPT] case_id  |  type  |  Status: ..."
  const CASE_RE = /\[([^\]]+)\]\s+(\S+)\s+\|\s+(.+?)\s+\|\s+Status:\s+(.+?)(\s+\|\s+⚠\s+\$([0-9,]+) outstanding)?$/
  const cases: CaseRow[] = []

  for (const line of lines) {
    const m = line.trim().match(CASE_RE)
    if (m) {
      cases.push({
        department: m[1].trim(),
        caseId: m[2].trim(),
        processType: m[3].trim(),
        status: m[4].trim(),
        feesOutstanding: m[6] ? parseFloat(m[6].replace(/,/g, '')) : null,
      })
    }
  }

  if (!apn && !address) return null

  return { address, apn, neighborhood, zoning, lotSize, currentUse, cases }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const DEPT_COLOURS: Record<string, string> = {
  LADBS: '#1c2253',
  'City Planning': '#7b5ea7',
}

const STATUS_COLOURS: Record<string, string> = {
  'Permit Finaled': '#089e00',
  'CofO Issued': '#089e00',
  Issued: '#089e00',
  'Ready to Issue': '#4caf50',
  'PC Approved': '#4caf50',
  'Corrections Needed': '#e07b00',
  'Recheck': '#e07b00',
  'PC on Hold': '#e07b00',
  'Fees Due': '#e07b00',
  'Intent to Revoke': '#ff0000',
  'Permit Revoked': '#ff0000',
  'PC Expired': '#ff0000',
  'Application Withdrawn': '#999',
  'Permit Withdrawn': '#999',
}

function statusColour(status: string): string {
  return STATUS_COLOURS[status] ?? '#555'
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function ZoningPill({ zoning }: { zoning: string }) {
  return <span className={styles.zoningPill}>{zoning}</span>
}

function DeptBadge({ dept }: { dept: string }) {
  const bg = DEPT_COLOURS[dept] ?? '#444'
  return (
    <span className={styles.deptBadge} style={{ background: bg }}>
      {dept}
    </span>
  )
}

function StatusDot({ status }: { status: string }) {
  const colour = statusColour(status)
  return (
    <span className={styles.statusCell}>
      <span className={styles.statusDot} style={{ background: colour }} aria-hidden="true" />
      <span style={{ color: colour }}>{status}</span>
    </span>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

interface Props {
  data: ParcelData
}

export default function ParcelCard({ data }: Props) {
  return (
    <div className={styles.card}>
      {/* Header */}
      <div className={styles.cardHeader}>
        <svg className={styles.pinIcon} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5S13.38 11.5 12 11.5z"/>
        </svg>
        <div className={styles.headerText}>
          <span className={styles.address}>{data.address}</span>
          {data.neighborhood && (
            <span className={styles.neighborhood}>{data.neighborhood}</span>
          )}
        </div>
      </div>

      {/* Property details */}
      <dl className={styles.detailGrid}>
        <div className={styles.detailItem}>
          <dt>APN</dt>
          <dd className={styles.mono}>{data.apn}</dd>
        </div>
        <div className={styles.detailItem}>
          <dt>Zoning</dt>
          <dd><ZoningPill zoning={data.zoning} /></dd>
        </div>
        {data.lotSize && (
          <div className={styles.detailItem}>
            <dt>Lot Size</dt>
            <dd>{data.lotSize}</dd>
          </div>
        )}
        {data.currentUse && (
          <div className={styles.detailItem}>
            <dt>Current Use</dt>
            <dd>{data.currentUse}</dd>
          </div>
        )}
      </dl>

      {/* Cases table */}
      {data.cases.length > 0 ? (
        <div className={styles.casesSection}>
          <h4 className={styles.casesHeading}>
            Cases
            <span className={styles.caseCount}>{data.cases.length}</span>
          </h4>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Dept</th>
                  <th>Case ID</th>
                  <th>Type</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.cases.map((c, i) => (
                  <tr key={i} className={c.feesOutstanding ? styles.feeRow : undefined}>
                    <td><DeptBadge dept={c.department} /></td>
                    <td className={styles.mono}>{c.caseId}</td>
                    <td>{c.processType}</td>
                    <td>
                      <StatusDot status={c.status} />
                      {c.feesOutstanding && (
                        <span className={styles.feeWarning}>
                          ⚠ ${c.feesOutstanding.toLocaleString()} owed
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <p className={styles.noCases}>No cases on record for this parcel.</p>
      )}
    </div>
  )
}
