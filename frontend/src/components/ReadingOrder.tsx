import type { PageView, RunView } from '../api/types'
import { withCodePoints } from './pageGeometry'

interface ReadingOrderProps {
  pages: PageView[]
  onRun?: (run: RunView) => void
}

/** What the model reads, in reading order, page by page; hidden runs are outlined and clickable. */
export function ReadingOrder({ pages, onRun }: ReadingOrderProps) {
  return (
    <div className="flex flex-col gap-4" data-testid="reading-order">
      {pages.map((page) => (
        <div key={page.number} className="flex flex-col gap-2">
          <div className="flex items-baseline justify-between border-b border-rule pb-1">
            <span className="eyebrow">Page {page.number}</span>
            <span className="text-[12px] text-ink-2">{page.runs.filter((r) => r.status === 'hidden').length} hidden</span>
          </div>
          <p className="m-0 font-mono text-[12.5px] leading-[1.8] text-ink">
            {page.runs.length === 0 ? <span className="text-ink-2">No text on this page.</span> : null}
            {page.runs.map((run, i) => {
              const text = withCodePoints(run.text)
              if (run.status === 'hidden' || run.status === 'benign-hidden') {
                return (
                  <button
                    type="button"
                    key={i}
                    className={`mr-1 cursor-pointer border-0 p-0 font-mono text-[12.5px] leading-[1.8] text-ink outline outline-1 outline-offset-2 ${run.status === 'hidden' ? 'bg-glass-2 outline-glass' : 'bg-transparent outline-dashed outline-ink-2'}`}
                    onClick={() => onRun?.(run)}
                    title={run.status === 'hidden' ? `Hidden: finding ${run.finding_id ?? ''}` : 'Benign-hidden'}
                  >
                    {text}
                  </button>
                )
              }
              return (
                <span key={i} className={`mr-1 ${run.status === 'unverified' ? 'text-ink-2' : ''}`}>
                  {text}
                </span>
              )
            })}
          </p>
        </div>
      ))}
    </div>
  )
}
