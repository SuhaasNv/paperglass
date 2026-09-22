import { useTechniques } from '../api/queries'
import type { Technique } from '../api/types'
import { errorMessage } from './errorMessage'

const FORMAT_ORDER = ['pdf', 'docx', 'text']

/** Techniques: the registry as a reference, one numeral per format. */
export function TechniquesPage() {
  const techniques = useTechniques()
  if (techniques.isPending) return <p className="px-5 py-16 text-ink-2 md:px-14">Loading the techniques.</p>
  if (techniques.isError) return <p role="alert" className="px-5 py-16 md:px-14">{errorMessage(techniques.error)}</p>

  const byFormat = new Map<string, Technique[]>()
  for (const t of techniques.data.techniques) {
    const format = t.formats[0] ?? 'other'
    byFormat.set(format, [...(byFormat.get(format) ?? []), t])
  }
  const formats = [...byFormat.keys()].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b))
  const total = techniques.data.techniques.length

  return (
    <section aria-labelledby="techniques-heading" className="flex flex-col gap-11 px-5 pt-10 pb-16 md:px-14 md:pt-14">
      <div className="rise d1 grid grid-cols-1 gap-6 md:grid-cols-12 md:items-end md:gap-x-6">
        <div className="flex flex-col gap-2.5 md:col-span-8">
          <span className="eyebrow">Reference · THREATS.md</span>
          <h1 id="techniques-heading" className="text-[56px] leading-[0.95] md:text-[96px]">{numberWord(total)} ways to hide.</h1>
          <p className="serif mt-2 max-w-[48ch] text-[18px] leading-[1.4] md:text-[21px]" data-testid="technique-count">{total} techniques. Each has one id, one plain sentence, a threshold, and a positive and a negative fixture in the repository. Nothing is covered that the fixtures do not prove.</p>
        </div>
        <div className="flex flex-col gap-2 border-l border-rule pl-5 text-[13px] text-ink-2 md:col-span-3 md:col-start-10">
          <span>Views: A extracted text · B rendered page · C structure</span><span>Stage: 0 parse · 1 raster ink check · 2 OCR on crops</span><span>Class: what a confirmed finding counts as</span>
        </div>
      </div>
      {formats.map((format) => {
        const rows = byFormat.get(format) ?? []
        return (
          <section key={format} aria-labelledby={`format-${format}`} className="grid grid-cols-1 gap-y-3.5 md:grid-cols-[120px_1fr] md:gap-x-6" data-reveal>
            <h2 id={`format-${format}`} className="ital text-[48px] leading-none md:text-[72px]">{format.toUpperCase()}</h2>
            <div className="flex flex-col gap-3">
              <div className="flex items-baseline justify-between border-b border-ink pb-2">
                <span className="eyebrow">{rows.length} techniques</span>
                <span className="text-[13px] text-ink-2">each with a positive and a negative fixture</span>
              </div>
              <div className="overflow-x-auto">
                <table>
                  <thead><tr><th>Technique id</th><th>Plain language</th><th>Threshold or mechanism</th><th>Views</th><th>Stage</th><th>Class</th><th>ATR</th></tr></thead>
                  <tbody>
                    {rows.map((t) => (
                      <tr key={t.id}>
                        <td className="w-[240px]"><code>{t.id}</code></td>
                        <td className="serif text-[18px] leading-[1.3] md:text-[19px]">{t.explanation}</td>
                        <td className="w-[280px] text-[13.5px] text-ink-2">{t.threshold}</td>
                        <td className="w-[60px] whitespace-nowrap">{t.views.join(', ')}</td>
                        <td className="w-[50px]">{t.stage}</td>
                        <td className="w-[140px] text-[13.5px]">{t.severity_class}{t.self_proving ? ', self-proving' : ''}</td>
                        <td className="w-[120px] text-[12px]">{t.atr_rule ? <code className="text-[11.5px]">{t.atr_rule}</code> : <span className="text-ink-2">none</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )
      })}
    </section>
  )
}

function rank(format: string): number {
  const i = FORMAT_ORDER.indexOf(format)
  return i === -1 ? FORMAT_ORDER.length : i
}

function numberWord(n: number): string {
  const words = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen', 'Twenty']
  return words[n] ?? String(n)
}
