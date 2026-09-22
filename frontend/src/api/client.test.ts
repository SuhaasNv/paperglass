import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, createScan, getScan, listTechniques } from './client'
import { jsonResponse, scanDetail } from '../test/render'

describe('api client', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('posts the file, tier and profile as multipart and returns the scan', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(scanDetail(), 201))
    vi.stubGlobal('fetch', fetchMock)
    const file = new File(['%PDF-1.4'], 'resume.pdf', { type: 'application/pdf' })

    const scan = await createScan({ file, tier: 'fast', profile: 'default' })

    expect(scan.id).toBe('abc123')
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/api/v1/scans')
    expect(init.method).toBe('POST')
    expect(init.credentials).toBe('include')
    const body = init.body as FormData
    expect(body.get('tier')).toBe('fast')
    expect(body.get('profile')).toBe('default')
    expect((body.get('file') as File).name).toBe('resume.pdf')
  })

  it('turns the standard error body into an ApiError', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse({ error: { code: 'not_found', message: 'No such scan.' } }, 404),
      ),
    )

    const error = await getScan('missing').catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(404)
    expect((error as ApiError).code).toBe('not_found')
    expect((error as ApiError).message).toBe('No such scan.')
  })

  it('still fails cleanly when the error body is not JSON', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response('<html>bad gateway</html>', { status: 502 })),
    )

    const error = await listTechniques().catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(502)
    expect((error as ApiError).code).toBe('http_error')
  })

  it('reports a network failure as status 0', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    const error = await listTechniques().catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(0)
    expect((error as ApiError).code).toBe('network')
  })

  it('escapes the scan id in the path', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(scanDetail()))
    vi.stubGlobal('fetch', fetchMock)

    await getScan('a/b')

    expect(fetchMock.mock.calls[0]?.[0]).toBe('/api/v1/scans/a%2Fb')
  })
})
