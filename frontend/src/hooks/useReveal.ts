import { useEffect } from 'react'

/**
 * Scroll-linked reveals: every element with data-reveal gets data-reveal-in (or data-reveal="in")
 * once 12 percent of it is visible, and keeps it. One observer per page; reduced motion shows
 * everything at once because the CSS transitions are off.
 */
export function useReveal(root: React.RefObject<HTMLElement | null>) {
  useEffect(() => {
    const scope = root.current
    if (scope === null || typeof IntersectionObserver === 'undefined') return
    const targets = Array.from(scope.querySelectorAll<HTMLElement>('[data-reveal]'))
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const el = entry.target as HTMLElement
          // React renders a bare data-reveal as "true"; plain reveals become "in", named ones keep their kind.
          const kind = el.dataset.reveal
          if (kind === '' || kind === 'true' || kind === 'in') el.dataset.reveal = 'in'
          el.dataset.revealIn = ''
          observer.unobserve(el)
        }
      },
      { threshold: 0.12 },
    )
    for (const t of targets) observer.observe(t)
    return () => observer.disconnect()
  }, [root])
}

/** The 1 px glass hairline under the header: how far down the document the reader is. */
export function useScrollProgress() {
  useEffect(() => {
    const set = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight
      const value = max > 0 ? window.scrollY / max : 0
      document.documentElement.style.setProperty('--progress', value.toFixed(4))
    }
    set()
    window.addEventListener('scroll', set, { passive: true })
    window.addEventListener('resize', set)
    return () => {
      window.removeEventListener('scroll', set)
      window.removeEventListener('resize', set)
    }
  }, [])
}
