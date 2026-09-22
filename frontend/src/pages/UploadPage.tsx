import { useRef, useState, type DragEvent, type FormEvent } from 'react'
import { useNavigate } from 'react-router'

import { useCreateScan, useProfiles } from '../api/queries'
import type { Tier } from '../api/types'
import { BrandMark } from '../components/BrandMark'
import { errorMessage } from './errorMessage'

const TIERS: Array<[Tier, string]> = [
  ['standard', 'Standard: structure, raster ink check, OCR on crops'],
  ['fast', 'Fast: structure and raster ink check'],
]
const ACCEPT = '.pdf,.docx,.txt,.md,.markdown'
const MAX_BYTES = 25 * 1024 * 1024

function humanSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1024))} KB`
}

/** Scan: one document, a tier, a profile, one action. The intake surface is a sheet on the desk. */
export function UploadPage() {
  const navigate = useNavigate()
  const create = useCreateScan()
  const profiles = useProfiles()
  const input = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [tier, setTier] = useState<Tier>('standard')
  const [profile, setProfile] = useState<string>('default')
  const [dragging, setDragging] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)

  function choose(next: File | null) {
    setLocalError(null)
    if (next !== null && next.size > MAX_BYTES) {
      setFile(null)
      setLocalError('That file is larger than the 25 MB limit.')
      return
    }
    setFile(next)
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setDragging(false)
    choose(event.dataTransfer.files[0] ?? null)
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (file === null) return
    create.mutate({ file, tier, profile }, { onSuccess: (scan) => void navigate(`/scans/${scan.id}`) })
  }

  const busy = create.isPending
  const error = localError ?? (create.isError ? errorMessage(create.error) : null)

  return (
    <section aria-labelledby="upload-heading" className="grid grid-cols-1 gap-y-10 px-5 pt-10 pb-16 md:grid-cols-12 md:gap-x-6 md:px-14 md:pt-16">
      <div className="flex flex-col gap-5 md:col-span-5">
        <div className="rise d1 eyebrow">Scan</div>
        <h1 id="upload-heading" className="rise d2 max-w-[9ch] text-[52px] leading-[0.95] md:text-[88px]">Put a document under the glass.</h1>
        <p className="rise d3 serif max-w-[30ch] text-[18px] leading-[1.4] md:text-[21px]">PDF, DOCX, plain text or Markdown. The verdict is one of four words, with every finding's evidence beside it.</p>
        <dl className="rise d4 mt-2 hidden border-t border-ink md:block">
          {([['View A', 'The text an extractor hands to the model.'], ['View B', 'The page as a person sees it: rendered, checked for ink, read by OCR.'], ['View C', 'Render modes, colours, sizes, clipping, layers, ActualText, Word runs.']] as const).map(([k, v]) => (
            <div key={k} className="grid grid-cols-[76px_1fr] gap-4 border-b border-rule py-3">
              <dt className="eyebrow pt-[3px]">{k}</dt>
              <dd className="m-0 text-[15px]">{v}</dd>
            </div>
          ))}
        </dl>
      </div>
      <form onSubmit={onSubmit} data-testid="upload-form" className="rise d3 flex flex-col gap-6 md:col-span-6 md:col-start-7">
        <div
          className={`relative flex h-[220px] -rotate-[0.5deg] flex-col items-center justify-center gap-3 border bg-white p-6 md:h-[320px] md:gap-3.5 md:p-8 ${dragging ? 'border-glass' : 'border-rule'}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          data-testid="dropzone"
        >
          <div className={`pointer-events-none absolute inset-3 border border-dashed md:inset-[18px] ${dragging ? 'border-glass' : 'border-rule'}`} />
          {busy ? <div className="scanline" aria-hidden="true" /> : null}
          <BrandMark size={40} className="text-ink" />
          {file === null ? (
            <>
              <div className="serif text-[24px] md:text-[30px]">Drop a document here</div>
              <div className="ital text-[16px] text-ink-2">or</div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-1">
              <code className="text-[15px]">{file.name}</code>
              <span className="text-[13px] text-ink-2">{humanSize(file.size)} · <button type="button" className="cursor-pointer border-0 bg-transparent p-0 text-[13px] text-glass underline underline-offset-[3px]" onClick={() => { choose(null); if (input.current) input.current.value = '' }}>remove</button></span>
            </div>
          )}
          <label htmlFor="file" className="btn-ghost h-[46px] bg-paper">{file === null ? 'Choose a file' : 'Choose another'}</label>
          <input
            id="file"
            ref={input}
            type="file"
            name="file"
            accept={ACCEPT}
            className="absolute h-px w-px overflow-hidden opacity-0"
            onChange={(event) => choose(event.target.files?.[0] ?? null)}
          />
          <div className="readout">PDF · DOCX · TXT · MD · up to 25 MB</div>
        </div>
        <div className="flex flex-col gap-6 md:flex-row">
          <div className="flex flex-col gap-2 md:w-[330px]">
            <label htmlFor="tier" className="eyebrow">Scan tier</label>
            <select id="tier" name="tier" className="field" value={tier} onChange={(e) => setTier(e.target.value as Tier)}>
              {TIERS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-2 md:w-[230px]">
            <label htmlFor="profile" className="eyebrow">Profile</label>
            <select id="profile" name="profile" className="field" value={profile} onChange={(e) => setProfile(e.target.value)}>
              {(profiles.data?.profiles ?? [{ name: 'default', version: '', description: '' }]).map((p) => (
                <option key={p.name} value={p.name} title={p.description}>{p.name}</option>
              ))}
            </select>
            <span className="text-[13px] text-ink-2">{profiles.data?.profiles.find((p) => p.name === profile)?.description ?? 'Thresholds as documented in THREATS.md.'}</span>
          </div>
        </div>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:gap-6">
          <button type="submit" className="btn" disabled={file === null || busy}>{busy ? 'Scanning' : 'Scan document'}</button>
          <span className="max-w-[44ch] text-[14px] text-ink-2">Your file is scanned in memory and not stored; the report is kept 7 days under an unguessable link.</span>
        </div>
        {busy ? <p className="text-[14px] text-ink-2">Rendering the pages and checking every run for ink.</p> : null}
        {error ? <p role="alert" className="border-l-2 border-critical pl-2.5 text-[15px]">{error}</p> : null}
      </form>
    </section>
  )
}
