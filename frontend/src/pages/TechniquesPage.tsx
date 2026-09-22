import { useTechniques } from '../api/queries'
import type { Technique } from '../api/types'
import { errorMessage } from './errorMessage'

const FORMAT_ORDER = ['pdf', 'docx', 'text']

/** Techniques: the registry as a reference, one section per format, plain sentence first. */
export function TechniquesPage() {
  const techniques = useTechniques()

  if (techniques.isPending) return <p>Loading the techniques.</p>
  if (techniques.isError) return <p role="alert">{errorMessage(techniques.error)}</p>

  const byFormat = new Map<string, Technique[]>()
  for (const technique of techniques.data.techniques) {
    const format = technique.formats[0] ?? 'other'
    byFormat.set(format, [...(byFormat.get(format) ?? []), technique])
  }
  const formats = [...byFormat.keys()].sort(
    (a, b) => rank(a) - rank(b) || a.localeCompare(b),
  )

  return (
    <section aria-labelledby="techniques-heading">
      <h1 id="techniques-heading">Techniques</h1>
      <p data-testid="technique-count">{techniques.data.techniques.length} techniques.</p>
      {formats.map((format) => (
        <section key={format} aria-labelledby={`format-${format}`}>
          <h2 id={`format-${format}`}>{format}</h2>
          <dl>
            {(byFormat.get(format) ?? []).map((technique) => (
              <div key={technique.id}>
                <dt>
                  <code>{technique.id}</code>
                </dt>
                <dd>
                  <p>{technique.explanation}</p>
                  <p>
                    {technique.threshold}. Views {technique.views.join(', ')}, stage{' '}
                    {technique.stage}
                    {technique.self_proving ? ', self-proving' : ''}. Class{' '}
                    {technique.severity_class}. Rule {technique.rule_version}.
                    {technique.atr_rule ? ` ATR ${technique.atr_rule}.` : ''}
                  </p>
                </dd>
              </div>
            ))}
          </dl>
        </section>
      ))}
    </section>
  )
}

function rank(format: string): number {
  const index = FORMAT_ORDER.indexOf(format)
  return index === -1 ? FORMAT_ORDER.length : index
}
