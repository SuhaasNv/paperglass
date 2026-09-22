import { useCallback, useRef, useState, type PointerEvent, type ReactNode } from 'react'

interface LensProps {
  /** What a person sees: the rendered page or crop. */
  page: ReactNode
  /** What the model reads, laid out at the same coordinates; shown inside the ring only. */
  reads: ReactNode
  className?: string
  style?: React.CSSProperties
  radius?: number
  label?: string
}

interface LensState {
  x: number
  y: number
  on: boolean
}

/**
 * The lens: a ring that follows the pointer while it is over a document, clipping the model's
 * text into view at the same place on the page. It exists nowhere else. On touch, a long press
 * opens it under the finger and lifting closes it.
 */
export function Lens({ page, reads, className, style, radius = 112, label = 'View A · model reads' }: LensProps) {
  const [state, setState] = useState<LensState>({ x: 0, y: 0, on: false })
  const surface = useRef<HTMLDivElement>(null)
  const pressTimer = useRef<number | null>(null)

  const place = useCallback((event: PointerEvent<HTMLDivElement>) => {
    const rect = event.currentTarget.getBoundingClientRect()
    return { x: event.clientX - rect.left, y: event.clientY - rect.top }
  }, [])

  const onMove = (event: PointerEvent<HTMLDivElement>) => {
    if (event.pointerType === 'touch' && !state.on) return
    setState({ ...place(event), on: true })
  }
  const onLeave = () => setState((s) => ({ ...s, on: false }))
  const onDown = (event: PointerEvent<HTMLDivElement>) => {
    if (event.pointerType !== 'touch') return
    const at = place(event)
    pressTimer.current = window.setTimeout(() => setState({ ...at, on: true }), 350)
  }
  const onUp = () => {
    if (pressTimer.current !== null) window.clearTimeout(pressTimer.current)
    pressTimer.current = null
    setState((s) => ({ ...s, on: false }))
  }

  return (
    <div
      ref={surface}
      className={`lens-surface relative select-none ${className ?? ''}`}
      style={style}
      data-testid="document"
      data-lens={state.on ? 'on' : 'off'}
      onPointerMove={onMove}
      onPointerLeave={onLeave}
      onPointerDown={onDown}
      onPointerUp={onUp}
      onPointerCancel={onUp}
    >
      {page}
      {state.on ? (
        <>
          <div
            className="pointer-events-none absolute inset-0"
            style={{ clipPath: `circle(${radius}px at ${state.x}px ${state.y}px)` }}
            aria-hidden="true"
          >
            {reads}
          </div>
          <div
            className="lens-ring"
            data-testid="lens-ring"
            style={{ left: state.x, top: state.y, width: radius * 2, height: radius * 2, margin: `-${radius}px 0 0 -${radius}px` }}
            aria-hidden="true"
          />
          <div className="lens-handle" style={{ left: state.x, top: state.y }} aria-hidden="true" />
          <div
            className="readout pointer-events-none absolute"
            style={{ left: state.x - radius, top: state.y - radius - 18, color: 'var(--color-glass)' }}
            aria-hidden="true"
          >
            {label}
          </div>
        </>
      ) : null}
    </div>
  )
}
