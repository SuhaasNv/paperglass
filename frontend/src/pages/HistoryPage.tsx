import { Link } from 'react-router'

import { useScans } from '../api/queries'
import { errorMessage } from './errorMessage'

/** History: the reports this browser made, newest first, as a table. Nothing else. */
export function HistoryPage() {
  const scans = useScans()

  if (scans.isPending) return <p>Loading your reports.</p>
  if (scans.isError) return <p role="alert">{errorMessage(scans.error)}</p>
  if (scans.data.scans.length === 0) {
    return (
      <section aria-labelledby="history-heading">
        <h1 id="history-heading">History</h1>
        <p>No reports yet. Reports are kept 7 days and belong to this browser.</p>
      </section>
    )
  }
  return (
    <section aria-labelledby="history-heading">
      <h1 id="history-heading">History</h1>
      <table data-testid="history">
        <thead>
          <tr>
            <th scope="col">Date</th>
            <th scope="col">File</th>
            <th scope="col">Verdict</th>
            <th scope="col">Tier</th>
          </tr>
        </thead>
        <tbody>
          {scans.data.scans.map((scan) => (
            <tr key={scan.id}>
              <td>{new Date(scan.created_at).toLocaleString()}</td>
              <td>
                <Link to={`/scans/${scan.id}`}>{scan.file_name}</Link>
              </td>
              <td>{scan.verdict}</td>
              <td>{scan.tier}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
