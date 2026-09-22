import { useEffect, useState } from 'react'

/** Copies a string; the label crossfades to Copied for 1.5 s. No toast. */
export function CopyButton({ text, small = false }: { text: string; small?: boolean }) {
  const [copied, setCopied] = useState(false)
  useEffect(() => {
    if (!copied) return
    const t = window.setTimeout(() => setCopied(false), 1500)
    return () => window.clearTimeout(t)
  }, [copied])
  return (
    <button
      type="button"
      className={`fade-swap shrink-0 border border-ink bg-transparent px-3 text-[11px] font-semibold uppercase tracking-[0.1em] ${small ? 'h-[34px]' : 'h-11'}`}
      onClick={() => {
        navigator.clipboard
          .writeText(text)
          .then(() => setCopied(true))
          .catch(() => setCopied(false))
      }}
    >
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}
