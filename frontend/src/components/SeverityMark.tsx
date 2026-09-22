import type { Severity } from '../api/types'

const COLOUR: Record<Severity, string> = {
  critical: 'var(--color-critical)',
  high: 'var(--color-high)',
  medium: 'var(--color-medium)',
  low: 'var(--color-low)',
  info: 'var(--color-ink-2)',
  'benign-hidden': 'var(--color-ink-2)',
}

/** The shape for a severity: label plus shape first, colour second (ACCESSIBILITY.md). */
export function SeverityShape({ level, size = 12 }: { level: Severity; size?: number }) {
  const c = COLOUR[level]
  const common = { width: size, height: size, viewBox: '0 0 12 12', 'aria-hidden': true as const }
  switch (level) {
    case 'critical':
      return (
        <svg {...common}>
          <polygon points="3.5,0.5 8.5,0.5 11.5,3.5 11.5,8.5 8.5,11.5 3.5,11.5 0.5,8.5 0.5,3.5" fill={c} />
        </svg>
      )
    case 'high':
      return (
        <svg {...common}>
          <polygon points="6,0.8 11.5,11.2 0.5,11.2" fill={c} />
        </svg>
      )
    case 'medium':
      return (
        <svg {...common}>
          <polygon points="6,0.5 11.5,6 6,11.5 0.5,6" fill={c} />
        </svg>
      )
    case 'low':
      return (
        <svg {...common}>
          <circle cx="6" cy="6" r="5.5" fill={c} />
        </svg>
      )
    case 'info':
      return (
        <svg {...common}>
          <circle cx="6" cy="6" r="5" fill="none" stroke={c} strokeWidth="1.4" />
        </svg>
      )
    case 'benign-hidden':
      return (
        <svg {...common}>
          <rect x="1" y="1" width="10" height="10" fill="none" stroke={c} strokeWidth="1.4" />
        </svg>
      )
  }
}

interface SeverityMarkProps {
  level: Severity
  label?: string
  size?: number
  strong?: boolean
}

/** Shape plus written label, the way every status appears in the app. */
export function SeverityMark({ level, label, size = 12, strong = false }: SeverityMarkProps) {
  return (
    <span
      className="inline-flex items-center gap-1.5 whitespace-nowrap text-[13px] tracking-[0.02em]"
      style={{ fontWeight: strong ? 600 : 500 }}
    >
      <SeverityShape level={level} size={size} />
      <span>{label ?? level}</span>
    </span>
  )
}
