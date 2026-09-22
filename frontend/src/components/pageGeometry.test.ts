import { describe, expect, it } from 'vitest'

import type { PageView } from '../api/types'
import { runBox, withCodePoints } from './pageGeometry'

const page: PageView = { number: 1, width_pt: 612, height_pt: 792, thumbnail: { data_uri: null, none_reason: 'test' }, runs: [] }

describe('page geometry', () => {
  it('maps a PDF box (origin bottom-left) to CSS percentages from the top', () => {
    const box = runBox({ text: 'x', bbox: { x0: 61.2, y0: 396, x1: 306, y1: 475.2 }, status: 'hidden', finding_id: 'f-1' }, page)
    expect(box).toEqual({ left: '10.000%', top: '40.000%', width: '40.000%', height: '10.000%' })
  })
  it('has no box without a position or a page size', () => {
    expect(runBox({ text: 'x', bbox: null, status: 'unverified', finding_id: null }, page)).toBeNull()
    expect(runBox({ text: 'x', bbox: { x0: 0, y0: 0, x1: 1, y1: 1 }, status: 'visible', finding_id: null }, { ...page, width_pt: null })).toBeNull()
  })
  it('shows invisible characters as code points', () => {
    expect(withCodePoints('a​b')).toBe('aU+200Bb')
    expect(withCodePoints('tag\u{E0041}')).toBe('tagU+E0041')
    expect(withCodePoints('plain')).toBe('plain')
  })
})
