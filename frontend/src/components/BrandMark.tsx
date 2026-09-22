interface BrandMarkProps {
  size?: number
  className?: string
}

/** A sheet of paper with a lens over its lower right corner. Works from 16 px up. */
export function BrandMark({ size = 20, className }: BrandMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      aria-hidden="true"
      className={className}
      style={{ flexShrink: 0 }}
    >
      <path d="M4 2.5h10l4 4V15" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M14 2.5v4h4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M4 2.5V21.5h6" fill="none" stroke="currentColor" strokeWidth="1.6" />
      <path d="M7 8.5h6M7 11.5h7M7 14.5h4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      <circle cx="15.5" cy="16.5" r="4.6" fill="var(--color-paper)" stroke="var(--color-glass)" strokeWidth="1.8" />
      <path d="M19 20l3.2 3.2" stroke="var(--color-glass)" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}
