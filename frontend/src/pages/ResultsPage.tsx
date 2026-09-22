import { useState } from 'react'
import { useParams } from 'react-router'

import { useFingerprintScan, useScan } from '../api/queries'
import type { Finding, RunView, ScanDetail, Severity } from '../api/types'
import { CopyButton } from '../components/CopyButton'
import { Lens } from '../components/Lens'
import { PageUnderGlass } from '../components/PageUnderGlass'
import { ReadingOrder } from '../components/ReadingOrder'
import { SeverityMark, SeverityShape } from '../components/SeverityMark'
import { errorMessage } from './errorMessage'

const LEVELS: Severity[] = ['critical', 'high', 'medium', 'low', 'info', 'benign-hidden']
const VERDICT_SHAPE: Record<string, Severity> = { malicious: 'critical', suspicious: 'medium', 'benign-hidden': 'benign-hidden', clean: 'info' }

function verdictSentence(scan: ScanDetail): string {
  const confirmed = scan.report.findings.filter((f) => f.status === 'confirmed')
  const top = confirmed[0]
  switch (scan.report.verdict) {
    case 'malicious':
      return `Hidden text found. ${confirmed.length === 1 ? 'One confirmed finding' : `${confirmed.length} confirmed findings`}${top ? ` at ${top.severity} severity` : ''}: text the model reads that the page does not show. The verdict follows from confirmed findings only.`
    case 'suspicious':
      return `Hidden text found. ${confirmed.length === 1 ? 'One confirmed finding' : `${confirmed.length} confirmed findings`}, none phrased as an instruction. The verdict follows from confirmed findings only.`
    case 'benign-hidden':
      return 'Hidden text found, all of it allowed by a public rule: alt text, ligature ActualText, an OCR layer on a scan. Nothing here is an attack.'
    default:
      return 'Nothing the model reads is missing from the page. Every extracted run left ink where the extractor said it would.'
  }
}

/** Results: the verdict line, the page under the glass, the findings with evidence, the fingerprint. */
export function ResultsPage() {
  const { id = '' } = useParams<{ id: string }>()
  const scan = useScan(id)
  if (scan.isPending) return <p className="px-5 py-16 text-ink-2 md:px-14">Loading the report.</p>
  if (scan.isError) return <p role="alert" className="px-5 py-16 md:px-14">{errorMessage(scan.error)}</p>
  return <Report scan={scan.data} />
}

function Report({ scan }: { scan: ScanDetail }) {
  const { report } = scan
  const unmatched = report.findings.filter((f) => f.status === 'confirmed' && f.extracted_text.trim())
  const confirmed = report.findings.filter((f) => f.status === 'confirmed').length
  const pages = report.pages ?? []
  const hiddenRuns = pages.length > 0 ? pages.reduce((n, p) => n + p.runs.filter((r) => r.status === 'hidden').length, 0) : unmatched.length
  const goToEvidence = (run: RunView) => {
    if (run.finding_id === null) return
    document.getElementById(run.finding_id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
  const shareUrl = typeof window !== 'undefined' ? window.location.href : ''
  return (
    <article aria-labelledby="results-heading" className="flex flex-col gap-14 px-5 pt-8 pb-14 md:px-14 md:pt-12">
      <section className="grid grid-cols-1 gap-y-6 md:grid-cols-12 md:gap-x-6">
        <div className="rise d1 flex flex-col gap-4 md:col-span-12 md:flex-row md:items-end md:justify-between">
          <div className="flex flex-col gap-2.5">
            <span className="eyebrow">Report · {scan.id} · {new Date(scan.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
            <h1 id="results-heading" className="text-[52px] leading-[0.95] break-words md:text-[96px]">{scan.file_name}</h1>
          </div>
          <div className="flex gap-5 text-[14px] md:pb-3">
            <CopyLink url={shareUrl} />
            <a href={`/api/v1/scans/${encodeURIComponent(scan.id)}/report.html`} download data-testid="download-report">Download HTML report</a>
            <button type="button" className="cursor-pointer border-0 bg-transparent p-0 text-[14px] text-glass underline underline-offset-[3px]" onClick={() => window.print()}>Print</button>
          </div>
        </div>
        <div className="rise d2 flex flex-col gap-3.5 border-t border-ink pt-4 md:col-span-7">
          <span className="eyebrow">Verdict</span>
          <div className="flex items-center gap-4" data-testid="verdict">
            <SeverityShape level={VERDICT_SHAPE[report.verdict] ?? 'info'} size={22} />
            <span className="serif text-[44px] leading-none tracking-[0.03em] md:text-[64px]">{report.verdict.toUpperCase()}</span>
          </div>
          <p className="serif max-w-[44ch] text-[18px] leading-[1.35] md:text-[22px]">{verdictSentence(scan)}</p>
          <div className="flex flex-wrap gap-x-5 gap-y-2 pt-1 text-[13px]">
            {LEVELS.map((l) => <SeverityMark key={l} level={l} label={`${l} ${report.severity_counts[l] ?? 0}`} />)}
          </div>
        </div>
        <div className="rise d3 grid grid-cols-2 gap-x-5 border-t border-ink pt-2 md:col-span-4 md:col-start-9">
          <Meta label="Format">{report.input_type}</Meta>
          <Meta label="Extractor" mono>{report.extractor}</Meta>
          <Meta label="Tier">{report.tier}</Meta>
          <Meta label="Profile">{report.profile}</Meta>
          <Meta label="Render-verified">{report.pages_render_verified} of {report.page_count}{report.dpi ? ` · ${report.dpi} dpi` : ''}</Meta>
          <Meta label="Tool" mono>paperglass {report.tool_version}</Meta>
          <Meta label="Expires">{new Date(scan.expires_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}</Meta>
          <Meta label="SHA-256" mono>{report.input_sha256.slice(0, 6)}…{report.input_sha256.slice(-6)}</Meta>
        </div>
      </section>

      <section aria-labelledby="glass-heading" className="rise d4 grid grid-cols-1 gap-y-5 md:grid-cols-12 md:gap-x-6">
        <div className="flex flex-col gap-2 border-b border-ink pb-3 md:col-span-12 md:flex-row md:items-baseline md:justify-between">
          <h2 id="glass-heading" className="text-[32px] md:text-[44px]">Under the glass</h2>
          <div className="text-[13px] text-ink-2">
            {hiddenRuns} hidden {hiddenRuns === 1 ? 'run' : 'runs'} · <span className="hidden md:inline">hover the page to read what the model reads</span><span className="md:hidden">press and hold the page to read what the model reads</span> · outlined runs open their evidence
          </div>
        </div>
        {pages.length > 0 ? (
          <>
            <div className="flex flex-col gap-8 md:col-span-7">
              {pages.map((page) => <PageUnderGlass key={page.number} page={page} onRun={goToEvidence} />)}
            </div>
            <div className="flex flex-col gap-4 md:col-span-5">
              <span className="eyebrow">What the model reads · reading order</span>
              <ReadingOrder pages={pages} onRun={goToEvidence} />
              <p className="text-[14px] leading-[1.55] text-ink-2">Outlined runs are the finding: text the extractor returned that left no ink on the page. Grey runs could not be checked (no raster). Characters that draw nothing are shown as their code points.</p>
            </div>
          </>
        ) : unmatched.length === 0 ? (
          <p className="text-[15px] text-ink-2 md:col-span-12">No confirmed hidden text on any page: there is nothing to put under the glass.</p>
        ) : (
          <>
            <div className="flex flex-col gap-6 md:col-span-7">
              {unmatched.map((f) => <Region key={f.id} finding={f} />)}
            </div>
            <div className="flex flex-col gap-4 md:col-span-5">
              <span className="eyebrow">Unmatched runs · what the model reads and the page does not show</span>
              <ol className="m-0 list-none p-0" data-testid="findings-summary">
                {unmatched.map((f) => (
                  <li key={f.id} className="flex flex-col gap-2 border-t border-ink py-4">
                    <div className="flex justify-between text-[13px]">
                      <span><span className="ital text-[18px]">{f.id.toUpperCase()}</span> · {f.page === null ? 'document' : `page ${f.page}`} · <code>{f.technique_id}</code></span>
                      <a href={`#${f.id}`} className="text-[13px]">evidence</a>
                    </div>
                    <blockquote className="serif m-0 border-l-2 border-glass bg-glass-2 px-3.5 py-2.5 text-[17px] leading-[1.35]">{f.extracted_text}</blockquote>
                  </li>
                ))}
              </ol>
              <p className="text-[14px] leading-[1.55] text-ink-2">This report predates page views (schema v1): each confirmed region is shown from its crop.</p>
            </div>
          </>
        )}
      </section>

      <section aria-labelledby="findings-heading" className="rise d5 flex flex-col">
        <div className="flex items-baseline justify-between border-b border-ink pb-3">
          <h2 id="findings-heading" className="text-[32px] md:text-[44px]">Findings</h2>
          <span className="text-[13px] text-ink-2">{report.findings.length} {report.findings.length === 1 ? 'finding' : 'findings'} · {confirmed} confirmed · {report.findings.length - confirmed} possible</span>
        </div>
        {report.findings.length === 0 ? (
          <p className="py-6 text-[15px] text-ink-2">No findings.</p>
        ) : (
          <ol className="m-0 list-none p-0" data-testid="findings">
            {report.findings.map((f) => <FindingItem key={f.id} finding={f} fileName={scan.file_name} />)}
          </ol>
        )}
      </section>

      <FingerprintSection scan={scan} />

      <section className="grid grid-cols-1 gap-8 md:grid-cols-2 md:gap-x-12">
        <div className="flex flex-col gap-2.5">
          <h2 className="border-b border-ink pb-2.5 text-[22px]">Parse failures</h2>
          {report.parse_failures.length === 0 ? (
            <p className="text-[15px] text-ink-2">None. Every parser call finished inside its limits.</p>
          ) : (
            <ul className="m-0 list-none p-0 text-[14px]" aria-label="Parse failures">
              {report.parse_failures.map((p, i) => <li key={i} className="border-b border-rule py-2"><code>{p.parser}</code> {p.reason} {p.message}</li>)}
            </ul>
          )}
        </div>
        <details className="border-b border-ink">
          <summary className="flex cursor-pointer list-none items-baseline justify-between pb-2.5">
            <h2 className="text-[22px]">Raw report JSON</h2>
            <span className="text-[13px] text-ink-2">schema v{report.schema_version}</span>
          </summary>
          <pre className="mb-4 max-h-[420px] overflow-auto bg-paper-2 px-5 py-4 text-[12.5px] leading-[1.6]">{JSON.stringify(report, null, 2)}</pre>
        </details>
      </section>
    </article>
  )
}

function CopyLink({ url }: { url: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      type="button"
      className="fade-swap cursor-pointer border-0 bg-transparent p-0 text-[14px] text-glass underline underline-offset-[3px]"
      onClick={() => { navigator.clipboard.writeText(url).then(() => setCopied(true)).catch(() => setCopied(false)); window.setTimeout(() => setCopied(false), 1500) }}
    >
      {copied ? 'Link copied' : 'Copy share link'}
    </button>
  )
}

function Meta({ label, mono = false, children }: { label: string; mono?: boolean; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-[3px] border-t border-rule py-2.5">
      <span className="eyebrow">{label}</span>
      {mono ? <code>{children}</code> : <span className="text-[15px]">{children}</span>}
    </div>
  )
}

/** One hidden region under the glass: the crop as the page, the extracted text inside the ring. */
function Region({ finding }: { finding: Finding }) {
  const where = finding.page === null ? 'document' : `page ${finding.page}`
  const crop = finding.render_crop.data_uri
  return (
    <div className="flex flex-col gap-2">
      <Lens
        className="h-[180px] w-full md:h-[220px]"
        radius={80}
        page={
          crop ? (
            <img src={crop} alt={`Rendered region of ${where} for ${finding.id}`} className="absolute inset-0 h-full w-full border border-rule bg-white object-contain" />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center border border-dashed border-rule text-[13px] text-ink-2">No render of this region ({finding.render_crop.none_reason ?? 'no reason given'}).</div>
          )
        }
        reads={
          <div className="absolute inset-0 flex items-center border border-glass bg-paper-2 px-5">
            <pre className="text-[12.5px] leading-[1.6]"><mark className="bg-glass-2 text-ink outline outline-1 outline-offset-2 outline-glass">{finding.extracted_text}</mark></pre>
          </div>
        }
      />
      <div className="flex justify-between text-[12px] text-ink-2">
        <span><span className="ital text-[16px] text-ink">{finding.id.toUpperCase()}</span> · {where}{report_dpi(finding)}</span>
        <span className="readout">{finding.render_crop.data_uri ? 'render verified' : 'no raster'}</span>
      </div>
    </div>
  )
}

function report_dpi(finding: Finding): string {
  return finding.bbox ? ` · bbox ${finding.bbox.x0.toFixed(1)} ${finding.bbox.y0.toFixed(1)} ${finding.bbox.x1.toFixed(1)} ${finding.bbox.y1.toFixed(1)} pt` : ''
}

function FindingItem({ finding, fileName }: { finding: Finding; fileName: string }) {
  const where = finding.page === null ? 'document' : `page ${finding.page}`
  const reproduce = finding.reproduce.replace('FILE', fileName)
  return (
    <li id={finding.id} className="grid grid-cols-1 gap-y-4 border-b border-rule py-8 md:grid-cols-[88px_1fr_360px] md:gap-x-8">
      <div className="flex flex-row items-baseline gap-3 md:flex-col md:gap-1.5">
        <span className="ital text-[32px] leading-none md:text-[40px]">{finding.id.toUpperCase()}</span>
        <span className="text-[13px] text-ink-2">{where}</span>
      </div>
      <div className="flex min-w-0 flex-col gap-3.5">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
          <SeverityMark level={finding.severity} size={14} strong />
          <span className={`text-[11px] font-semibold tracking-[0.14em] uppercase ${finding.status === 'confirmed' ? 'text-ink' : 'text-ink-2'}`}>{finding.status}</span>
          <code>{finding.technique_id}</code>
          <span className="text-[13px] text-ink-2">confidence {finding.confidence.toFixed(2)} · views {finding.views.join(', ')} · stage {finding.stage}</span>
        </div>
        <p className="serif max-w-[24ch] text-[24px] leading-[1.2] md:text-[28px]">{finding.why_hidden}</p>
        <div className="grid grid-cols-1 gap-y-2 text-[14px] md:grid-cols-[110px_1fr] md:gap-x-4 md:gap-y-2.5">
          {finding.extracted_text.trim() ? (
            <>
              <span className="eyebrow pt-[3px]">Hidden text</span>
              <blockquote className="serif m-0 border-l-2 border-glass bg-glass-2 px-3 py-2 text-[17px] leading-[1.35]">{finding.extracted_text}</blockquote>
            </>
          ) : null}
          <span className="eyebrow pt-[3px]">Mechanism</span>
          <code className="leading-[1.6]">{finding.mechanism}</code>
          <span className="eyebrow pt-[3px]">Reproduce</span>
          <div className="flex min-w-0 items-center gap-3">
            <code className="min-w-0 grow bg-paper-2 px-2.5 py-1.5 break-all">{reproduce}</code>
            <CopyButton text={reproduce} small />
          </div>
          <span className="eyebrow pt-[3px]">Class</span>
          <span>{finding.severity_class}{finding.atr_rule ? ` · ${finding.atr_rule}` : ''}</span>
        </div>
      </div>
      <figure className={`m-0 flex flex-col gap-2.5 ${finding.render_crop.data_uri ? 'lift' : ''}`}>
        {finding.render_crop.data_uri ? (
          <img src={finding.render_crop.data_uri} alt={`Rendered crop of ${where}`} className="h-[128px] w-full border border-rule bg-white object-contain" />
        ) : (
          <div className="flex h-[128px] items-center justify-center border border-dashed border-rule p-4 text-center text-[13px] text-ink-2">No crop: {finding.render_crop.none_reason ?? 'this finding has no region on the page'}.</div>
        )}
        <figcaption className="text-[13px] leading-[1.5] text-ink-2">Evidence {finding.id.toUpperCase()} · {where}{finding.bbox ? `, region ${finding.bbox.x0.toFixed(0)} ${finding.bbox.y0.toFixed(0)} ${finding.bbox.x1.toFixed(0)} ${finding.bbox.y1.toFixed(0)} pt` : ''}</figcaption>
      </figure>
    </li>
  )
}

function FingerprintSection({ scan }: { scan: ScanDetail }) {
  const fingerprint = useFingerprintScan(scan.id)
  const [file, setFile] = useState<File | null>(null)
  const table = scan.fingerprint
  const extractors = table ? Object.keys(table.extractors) : []
  return (
    <section aria-labelledby="fingerprint-heading" className="flex flex-col gap-4">
      <div className="flex flex-col gap-2 border-b border-ink pb-3 md:flex-row md:items-baseline md:justify-between">
        <h2 id="fingerprint-heading" className="text-[32px] md:text-[44px]">Fingerprint</h2>
        <span className="text-[13px] text-ink-2">{table ? `${extractors.length} extractors ran` : 'not run yet'}</span>
      </div>
      {table === null ? (
        <form
          className="flex flex-col gap-4"
          onSubmit={(event) => { event.preventDefault(); if (file !== null) fingerprint.mutate(file) }}
        >
          <p className="max-w-[72ch] text-[15px]">Which installed PDF extractors hand each hidden run to a model. The file is not stored, so choose it again; the SHA-256 must match the report.</p>
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <label htmlFor="fingerprint-file" className="btn-ghost h-[46px]">{file === null ? 'Choose the same file' : file.name}</label>
            <input id="fingerprint-file" type="file" name="file" className="absolute h-px w-px overflow-hidden opacity-0" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            <button type="submit" className="btn" disabled={file === null || fingerprint.isPending}>{fingerprint.isPending ? 'Running' : 'Fingerprint'}</button>
          </div>
          {fingerprint.isError ? <p role="alert" className="border-l-2 border-critical pl-2.5 text-[15px]">{errorMessage(fingerprint.error)}</p> : null}
        </form>
      ) : (
        <div className="overflow-x-auto">
          <table data-testid="fingerprint">
            <thead>
              <tr>
                <th>Finding</th><th>Technique</th>
                {extractors.map((n) => <th key={n} scope="col">{n} {table.extractors[n]}</th>)}
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row) => (
                <tr key={row.finding_id}>
                  <td><span className="ital text-[18px]">{row.finding_id.toUpperCase()}</span></td>
                  <td><code>{row.technique_id}</code><div className="mt-0.5 text-[13px] text-ink-2">{row.text_preview}</div></td>
                  {extractors.map((n) => {
                    const v = row.extractors.find((e) => e.extractor === n)
                    if (v === undefined || v.returns_hidden_text === null) return <td key={n}><SeverityMark level="benign-hidden" label="failed" /></td>
                    return <td key={n}>{v.returns_hidden_text ? <SeverityMark level="critical" label="fooled" /> : <SeverityMark level="info" label="clean" />}</td>
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex flex-wrap gap-x-7 gap-y-2 pt-3 text-[13px] text-ink-2">
            <SeverityMark level="critical" label="fooled: returns the hidden text" /><SeverityMark level="info" label="clean: does not return it" /><SeverityMark level="benign-hidden" label="failed: the extractor raised" />
          </div>
        </div>
      )}
    </section>
  )
}
