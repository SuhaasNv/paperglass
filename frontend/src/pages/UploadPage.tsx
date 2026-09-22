import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router'

import { useCreateScan } from '../api/queries'
import type { Tier } from '../api/types'
import { errorMessage } from './errorMessage'

const TIERS: Tier[] = ['fast', 'standard']
const PROFILES = ['default']
const ACCEPT = '.pdf,.docx,.txt,.md,.markdown'

/**
 * Upload: one file, a tier, a profile, one action. On success the browser moves to the
 * report. Plumbing: the design pass owns the drop zone and the copy.
 */
export function UploadPage() {
  const navigate = useNavigate()
  const create = useCreateScan()
  const [file, setFile] = useState<File | null>(null)
  const [tier, setTier] = useState<Tier>('standard')
  const [profile, setProfile] = useState<string>('default')

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (file === null) return
    create.mutate(
      { file, tier, profile },
      { onSuccess: (scan) => void navigate(`/scans/${scan.id}`) },
    )
  }

  return (
    <section aria-labelledby="upload-heading">
      <h1 id="upload-heading">Scan a document</h1>
      <form onSubmit={onSubmit} data-testid="upload-form">
        <label>
          File
          <input
            type="file"
            name="file"
            accept={ACCEPT}
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <label>
          Tier
          <select name="tier" value={tier} onChange={(event) => setTier(event.target.value as Tier)}>
            {TIERS.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <label>
          Profile
          <select name="profile" value={profile} onChange={(event) => setProfile(event.target.value)}>
            {PROFILES.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={file === null || create.isPending}>
          {create.isPending ? 'Scanning' : 'Scan'}
        </button>
        <p>
          Your file is scanned in memory and not stored; the report is kept 7 days under an
          unguessable link.
        </p>
        {create.isError ? <p role="alert">{errorMessage(create.error)}</p> : null}
      </form>
    </section>
  )
}
