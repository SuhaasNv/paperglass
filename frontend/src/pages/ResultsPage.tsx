import { useState } from 'react'
import { useParams } from 'react-router'

import { useFingerprintScan, useScan } from '../api/queries'
import type { Finding, ScanDetail } from '../api/types'
import { errorMessage } from './errorMessage'

/**
 * Results: the verdict line, the findings with their evidence, the fingerprint on request.
 * Plumbing: the diff view, the crops and the tabs arrive with the design pass.
 */
export function ResultsPage() {
  const { id = '' } = useParams<{ id: string }>()
  const scan = useScan(id)

  if (scan.isPending) return <p>Loading the report.</p>
  if (scan.isError) return <p role="alert">{errorMessage(scan.error)}</p>
  return <Report scan={scan.data} />
}

function Report({ scan }: { scan: ScanDetail }) {
  const { report } = scan
  const counts = Object.entries(report.severity_counts)
    .filter(([, n]) => n > 0)
    .map(([level, n]) => `${level} ${n}`)
    .join(', ')
  return (
    <article aria-labelledby="results-heading">
      <h1 id="results-heading">{scan.file_name}</h1>
      <p data-testid="verdict">
        Verdict: <strong>{report.verdict}</strong>
        {counts ? ` (${counts})` : ''}
      </p>
      <p>
        {report.input_type} via {report.extractor}, tier {report.tier}, profile {report.profile},
        pages {report.pages_render_verified} of {report.page_count} render-verified
        {report.dpi ? ` at ${report.dpi} dpi` : ''}. Tool {report.tool_version}. Expires{' '}
        {new Date(scan.expires_at).toLocaleString()}.
      </p>
      {report.parse_failures.length > 0 ? (
        <ul aria-label="Parse failures">
          {report.parse_failures.map((failure, index) => (
            <li key={index}>
              parse failure: {failure.parser} {failure.reason} {failure.message}
            </li>
          ))}
        </ul>
      ) : null}
      <h2>Findings</h2>
      {report.findings.length === 0 ? (
        <p>No findings.</p>
      ) : (
        <ol data-testid="findings">
          {report.findings.map((finding) => (
            <FindingItem key={finding.id} finding={finding} fileName={scan.file_name} />
          ))}
        </ol>
      )}
      <FingerprintSection scan={scan} />
      <details>
        <summary>Report JSON</summary>
        <pre>{JSON.stringify(report, null, 2)}</pre>
      </details>
    </article>
  )
}

function FindingItem({ finding, fileName }: { finding: Finding; fileName: string }) {
  const where = finding.page === null ? 'document' : `page ${finding.page}`
  return (
    <li>
      <p>
        {finding.severity} {finding.status} <code>{finding.technique_id}</code> ({where},
        confidence {finding.confidence.toFixed(2)})
      </p>
      <p>{finding.why_hidden}</p>
      <p>
        mechanism: <code>{finding.mechanism}</code>
      </p>
      <p>
        reproduce: <code>{finding.reproduce.replace('FILE', fileName)}</code>
      </p>
      {finding.extracted_text.trim() ? <blockquote>{finding.extracted_text}</blockquote> : null}
      {finding.render_crop.data_uri ? (
        <img src={finding.render_crop.data_uri} alt={`Rendered crop of ${where}`} />
      ) : (
        <p>crop: none ({finding.render_crop.none_reason ?? 'no reason given'})</p>
      )}
    </li>
  )
}

function FingerprintSection({ scan }: { scan: ScanDetail }) {
  const fingerprint = useFingerprintScan(scan.id)
  const [file, setFile] = useState<File | null>(null)
  const table = scan.fingerprint

  return (
    <section aria-labelledby="fingerprint-heading">
      <h2 id="fingerprint-heading">Fingerprint</h2>
      {table === null ? (
        <form
          onSubmit={(event) => {
            event.preventDefault()
            if (file !== null) fingerprint.mutate(file)
          }}
        >
          <p>
            Which installed extractors hand the hidden text to a model. The file is not stored, so
            choose it again.
          </p>
          <label>
            File
            <input
              type="file"
              name="file"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <button type="submit" disabled={file === null || fingerprint.isPending}>
            {fingerprint.isPending ? 'Running' : 'Fingerprint'}
          </button>
          {fingerprint.isError ? <p role="alert">{errorMessage(fingerprint.error)}</p> : null}
        </form>
      ) : (
        <table data-testid="fingerprint">
          <thead>
            <tr>
              <th scope="col">Finding</th>
              <th scope="col">Technique</th>
              <th scope="col">Page</th>
              {Object.keys(table.extractors).map((name) => (
                <th scope="col" key={name}>
                  {name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row) => (
              <tr key={row.finding_id}>
                <td>{row.finding_id}</td>
                <td>
                  <code>{row.technique_id}</code>
                </td>
                <td>{row.page ?? '-'}</td>
                {Object.keys(table.extractors).map((name) => {
                  const verdict = row.extractors.find((v) => v.extractor === name)
                  const mark =
                    verdict === undefined || verdict.returns_hidden_text === null
                      ? 'failed'
                      : verdict.returns_hidden_text
                        ? 'fooled'
                        : 'clean'
                  return <td key={name}>{mark}</td>
                })}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
