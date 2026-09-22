import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { fetchWithProfiles, jsonResponse, maliciousReport, renderAt, scanDetail } from '../test/render'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('routes', () => {
  it('renders the upload form at the root', () => {
    renderAt('/')
    expect(screen.getByRole('heading', { name: 'Scan a document' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Scan' })).toBeDisabled()
  })

  it('renders about without the network', () => {
    renderAt('/about')
    expect(screen.getByRole('heading', { name: 'About Paperglass' })).toBeInTheDocument()
  })

  it('renders not found for an unknown path', () => {
    renderAt('/nowhere')
    expect(screen.getByRole('heading', { name: 'Not found' })).toBeInTheDocument()
  })
})

describe('upload', () => {
  it('scans the chosen file and moves to the report', async () => {
    const detail = scanDetail({ id: 'xyz', verdict: 'malicious', report: maliciousReport })
    const scans = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(detail, 201)))
    const fetchMock = vi.fn().mockImplementation(fetchWithProfiles(scans))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()
    const { router } = renderAt('/')

    const file = new File(['%PDF-1.4'], 'resume.pdf', { type: 'application/pdf' })
    await user.upload(screen.getByLabelText('File'), file)
    await user.selectOptions(screen.getByLabelText('Tier'), 'fast')
    await screen.findByRole('option', { name: 'resume' })
    await user.selectOptions(screen.getByLabelText('Profile'), 'resume')
    await user.click(screen.getByRole('button', { name: 'Scan' }))

    await waitFor(() => expect(router.state.location.pathname).toBe('/scans/xyz'))
    expect(await screen.findByTestId('verdict')).toHaveTextContent('malicious')
    expect(screen.getByTestId('findings').querySelectorAll('li')).toHaveLength(1)
    expect(screen.getByText(/paperglass show --page 1 --instruction 9 resume.pdf/)).toBeInTheDocument()
    // The report came back from the mutation; the results page did not fetch it again.
    expect(scans).toHaveBeenCalledTimes(1)
    const [, init] = scans.mock.calls[0] as [string, RequestInit]
    expect((init.body as FormData).get('profile')).toBe('resume')
  })

  it('shows the server message when the upload is refused', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(
        fetchWithProfiles(() =>
          Promise.resolve(
            jsonResponse({ error: { code: 'upload_too_large', message: 'The file is 30 MB; the limit is 25 MB.' } }, 413),
          ),
        ),
      ),
    )
    const user = userEvent.setup()
    renderAt('/')

    await user.upload(screen.getByLabelText('File'), new File(['x'], 'big.pdf'))
    await user.click(screen.getByRole('button', { name: 'Scan' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('The file is 30 MB; the limit is 25 MB.')
  })
})

describe('results', () => {
  it('fetches a shared report by id and explains an expired one', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ error: { code: 'not_found', message: 'gone' } }, 404)),
    )
    renderAt('/scans/old')
    expect(await screen.findByRole('alert')).toHaveTextContent('This report does not exist or has expired.')
  })

  it('runs the fingerprint on the re-uploaded file and shows the table', async () => {
    const fingerprinted = scanDetail({
      fingerprint: {
        input_sha256: 'a'.repeat(64),
        input_type: 'pdf',
        default_extractor: 'pypdfium2',
        extractors: { pypdfium2: '4.30', pypdf: '5.1' },
        failed: {},
        rows: [
          {
            finding_id: 'f-1',
            technique_id: 'pdf.text.low_contrast',
            page: 1,
            text_preview: 'Note to the model',
            extractors: [
              { extractor: 'pypdfium2', version: '4.30', returns_hidden_text: true, agreement: 1 },
              { extractor: 'pypdf', version: '5.1', returns_hidden_text: null, agreement: 0 },
            ],
          },
        ],
      },
    })
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(scanDetail()))
      .mockResolvedValueOnce(jsonResponse(fingerprinted))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()
    renderAt('/scans/abc123')

    await screen.findByTestId('verdict')
    const section = screen.getByRole('region', { name: 'Fingerprint' })
    await user.upload(section.querySelector('input[type=file]') as HTMLInputElement, new File(['x'], 'resume.pdf'))
    await user.click(screen.getByRole('button', { name: 'Fingerprint' }))

    const table = await screen.findByTestId('fingerprint')
    expect(table).toHaveTextContent('fooled')
    expect(table).toHaveTextContent('failed')
    expect(fetchMock.mock.calls[1]?.[0]).toBe('/api/v1/scans/abc123/fingerprint')
  })
})

describe('history and techniques', () => {
  it('lists this browser\'s scans with a link to each report', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ scans: [scanDetail(), scanDetail({ id: 'second', file_name: 'cv.docx', verdict: 'suspicious' })] })),
    )
    renderAt('/history')

    const table = await screen.findByTestId('history')
    expect(table.querySelectorAll('tbody tr')).toHaveLength(2)
    expect(screen.getByRole('link', { name: 'cv.docx' })).toHaveAttribute('href', '/scans/second')
  })

  it('says so when there is no history', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ scans: [] })))
    renderAt('/history')
    expect(await screen.findByText(/No reports yet/)).toBeInTheDocument()
  })

  it('groups techniques by format', async () => {
    const technique = {
      formats: ['pdf'],
      views: ['C'],
      stage: 0,
      self_proving: true,
      severity_class: 'data',
      explanation: 'Text on a layer that is switched off',
      threshold: 'OCG off',
      atr_rule: null,
      rule_version: '1',
      release: 'v0.1.0',
    }
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse({
          techniques: [
            { ...technique, id: 'pdf.layer.hidden' },
            { ...technique, id: 'docx.run.vanish', formats: ['docx'] },
            { ...technique, id: 'text.unicode.invisible', formats: ['text', 'pdf', 'docx'] },
          ],
        }),
      ),
    )
    renderAt('/techniques')

    expect(await screen.findByTestId('technique-count')).toHaveTextContent('3 techniques')
    const headings = screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)
    expect(headings).toEqual(['pdf', 'docx', 'text'])
  })
})
