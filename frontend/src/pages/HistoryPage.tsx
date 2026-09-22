import { Link } from 'react-router'

import { useScans } from '../api/queries'
import type { Severity, Verdict } from '../api/types'
import { SeverityMark } from '../components/SeverityMark'
import { errorMessage } from './errorMessage'

const SHAPE: Record<Verdict, Severity | null> = { malicious: 'critical', suspicious: 'medium', 'benign-hidden': 'benign-hidden', clean: null }

/** History: the reports this browser made, as an archive index. */
export function HistoryPage() {
  const scans = useScans()
  if (scans.isPending) return <p className="px-5 py-16 text-ink-2 md:px-14">Loading your reports.</p>
  if (scans.isError) return <p role="alert" className="px-5 py-16 md:px-14">{errorMessage(scans.error)}</p>
  const rows = scans.data.scans
  return (
    <section aria-labelledby="history-heading" className="flex flex-col gap-7 px-5 pt-10 pb-16 md:px-14 md:pt-14">
      <div className="rise d1 flex flex-col gap-2.5 md:flex-row md:items-end md:justify-between">
        <div className="flex flex-col gap-2.5">
          <span className="eyebrow">Archive · this browser</span>
          <h1 id="history-heading" className="text-[64px] leading-[0.95] md:text-[96px]">History</h1>
        </div>
        {rows.length > 0 ? <span className="text-[13px] text-ink-2 md:pb-3.5">{rows.length} {rows.length === 1 ? 'report' : 'reports'} · kept 7 days</span> : null}
      </div>
      {rows.length === 0 ? (
        <div className="rise d2 grid grid-cols-1 gap-4 border-t border-ink pt-5 md:grid-cols-12 md:gap-x-6">
          <div className="flex flex-col gap-2.5 md:col-span-6 md:col-start-3">
            <h2 className="text-[36px] md:text-[44px]">Nothing under the glass yet.</h2>
            <p className="text-[15px] text-ink-2">Reports are kept 7 days and belong to this browser.</p>
            <div><Link to="/scan" className="btn h-11">Scan a document</Link></div>
          </div>
        </div>
      ) : (
        <>
          <div className="rise d2 overflow-x-auto">
            <table data-testid="history">
              <thead>
                <tr><th className="w-[190px]">Date</th><th>File</th><th className="w-[170px]">Verdict</th><th className="w-[110px]">Tier</th><th className="w-[130px]">Profile</th><th className="w-[120px] text-right">Link</th></tr>
              </thead>
              <tbody>
                {rows.map((scan) => {
                  const shape = SHAPE[scan.verdict]
                  return (
                    <tr key={scan.id}>
                      <td className="whitespace-nowrap font-mono text-[12.5px] text-ink-2">{new Date(scan.created_at).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</td>
                      <td><Link to={`/scans/${scan.id}`} className="serif text-[20px] text-ink no-underline md:text-[22px]">{scan.file_name}</Link></td>
                      <td>{shape ? <SeverityMark level={shape} label={scan.verdict} /> : <span className="text-[13px] font-medium tracking-[0.04em]">{scan.verdict}</span>}</td>
                      <td>{scan.tier}</td>
                      <td>{scan.profile}</td>
                      <td className="text-right"><Link to={`/scans/${scan.id}`} className="text-[13px]">Open report</Link></td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <p className="max-w-[72ch] text-[14px] text-ink-2">Reports belong to the browser that made them and are removed 7 days after the scan. A report's link works for anyone who has it; the file itself was never kept.</p>
        </>
      )}
    </section>
  )
}
