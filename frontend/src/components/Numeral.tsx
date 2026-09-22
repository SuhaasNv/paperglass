/** The italic roman numeral that heads a landing section and darkens as the section arrives. */
export function Numeral({ children, light = false }: { children: string; light?: boolean }) {
  return (
    <span
      className="ital block text-[64px] leading-none md:text-[96px]"
      data-reveal="numeral"
      style={{ color: light ? 'var(--color-paper)' : 'var(--color-ink)' }}
    >
      {children}
    </span>
  )
}
