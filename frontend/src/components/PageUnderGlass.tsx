import type { PageView, RunView } from '../api/types'
import { Lens } from './Lens'
import { runBox } from './pageGeometry'

interface PageUnderGlassProps {
  page: PageView
  onRun?: (run: RunView) => void
}

/**
 * The real page under the glass: the thumbnail is what a person sees; inside the ring, every
 * extracted run drawn at its own box, hidden runs outlined. Marks for hidden runs stay visible
 * outside the ring so the reader knows where to look.
 */
export function PageUnderGlass({ page, onRun }: PageUnderGlassProps) {
  const ratio = page.width_pt && page.height_pt ? page.height_pt / page.width_pt : 1.294
  const hidden = page.runs.filter((r) => r.status === 'hidden' || r.status === 'benign-hidden')
  const thumb = page.thumbnail.data_uri
  return (
    <div className="flex flex-col gap-2" data-testid={`page-${page.number}`}>
      <Lens
        className="w-full"
        style={{ aspectRatio: `1 / ${ratio}` }}
        radius={96}
        page={
          <>
            {thumb ? (
              <img src={thumb} alt={`Page ${page.number} as rendered`} className="absolute inset-0 h-full w-full border border-rule bg-white object-fill" />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center border border-dashed border-rule bg-paper-2 p-6 text-center text-[13px] text-ink-2">
                No render of page {page.number} ({page.thumbnail.none_reason ?? 'no reason given'}); the runs are listed beside it.
              </div>
            )}
            {hidden.map((run, i) => {
              const box = runBox(run, page)
              if (box === null) return null
              return (
                <button
                  type="button"
                  key={i}
                  className="absolute cursor-pointer border-0 bg-glass-2/60 p-0 outline outline-1 outline-offset-2 outline-glass"
                  style={box}
                  aria-label={`${run.status === 'hidden' ? 'Hidden' : 'Benign-hidden'} run ${run.finding_id ?? ''}: ${run.text.slice(0, 80)}`}
                  onClick={() => onRun?.(run)}
                  data-testid="hidden-run"
                />
              )
            })}
          </>
        }
        reads={
          <div className="absolute inset-0 border border-glass bg-paper-2">
            {page.runs.map((run, i) => {
              const box = runBox(run, page)
              if (box === null) return null
              const fontSize = `calc(${box.height} * 0.72)`
              return (
                <span
                  key={i}
                  className={`absolute overflow-hidden font-mono leading-none whitespace-nowrap text-ink ${run.status === 'hidden' ? 'bg-glass-2 outline outline-1 outline-glass' : run.status === 'benign-hidden' ? 'outline outline-1 outline-dashed outline-ink-2' : ''}`}
                  style={{ ...box, fontSize, containerType: 'size' }}
                >
                  {run.text}
                </span>
              )
            })}
          </div>
        }
      />
      <div className="flex justify-between text-[12px] text-ink-2">
        <span>page {page.number}{page.width_pt && page.height_pt ? ` · ${Math.round(page.width_pt)} by ${Math.round(page.height_pt)} pt` : ''} · {page.runs.length} runs · {hidden.length} hidden</span>
        <span className="readout">{thumb ? 'render verified' : 'no raster'}</span>
      </div>
    </div>
  )
}
