import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Lens } from './Lens'

describe('the lens', () => {
  it('appears only while the pointer is over the document', () => {
    render(<Lens page={<div>page</div>} reads={<div>reads</div>} />)
    const doc = screen.getByTestId('document')
    expect(screen.queryByTestId('lens-ring')).toBeNull()
    expect(doc).toHaveAttribute('data-lens', 'off')

    fireEvent.pointerMove(doc, { clientX: 40, clientY: 30, pointerType: 'mouse' })
    expect(screen.getByTestId('lens-ring')).toBeInTheDocument()
    expect(doc).toHaveAttribute('data-lens', 'on')
    expect(screen.getByText('reads')).toBeInTheDocument()

    fireEvent.pointerLeave(doc)
    expect(screen.queryByTestId('lens-ring')).toBeNull()
    expect(doc).toHaveAttribute('data-lens', 'off')
  })

  it('does not open on a touch move without a long press', () => {
    render(<Lens page={<div>page</div>} reads={<div>reads</div>} />)
    const doc = screen.getByTestId('document')
    fireEvent.pointerMove(doc, { clientX: 40, clientY: 30, pointerType: 'touch' })
    expect(screen.queryByTestId('lens-ring')).toBeNull()
  })
})
