import type { PageView, RunView } from '../api/types'

/** Percent box of a run on the page: PDF points, origin bottom-left, to CSS percentages. */
export function runBox(run: RunView, page: PageView): { left: string; top: string; width: string; height: string } | null {
  if (run.bbox === null || page.width_pt === null || page.height_pt === null) return null
  const w = page.width_pt
  const h = page.height_pt
  return {
    left: `${((run.bbox.x0 / w) * 100).toFixed(3)}%`,
    top: `${(((h - run.bbox.y1) / h) * 100).toFixed(3)}%`,
    width: `${(((run.bbox.x1 - run.bbox.x0) / w) * 100).toFixed(3)}%`,
    height: `${(((run.bbox.y1 - run.bbox.y0) / h) * 100).toFixed(3)}%`,
  }
}

const INVISIBLE = /[\u200B-\u200F\u202A-\u202E\u2060-\u2064\u2066-\u2069\uFEFF]|[\u{E0000}-\u{E007F}]/gu

/** Show characters that draw nothing as their code points, so the reader can see them. */
export function withCodePoints(text: string): string {
  return text.replace(INVISIBLE, (ch) => `U+${(ch.codePointAt(0) ?? 0).toString(16).toUpperCase().padStart(4, '0')}`)
}

