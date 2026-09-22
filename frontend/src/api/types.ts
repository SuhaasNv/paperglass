/**
 * Shapes of the backend responses (backend/app/api/schemas.py) and of the library's
 * Report JSON (schemas/report-v1.json). Kept by hand and checked by the e2e journey;
 * a field added on the server is added here in the same change.
 */

export type Verdict = 'clean' | 'benign-hidden' | 'suspicious' | 'malicious'
export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info' | 'benign-hidden'
export type SeverityClass = 'instruction' | 'data' | 'benign-hidden' | 'structure-only'
export type FindingStatus = 'possible' | 'confirmed'
export type Tier = 'fast' | 'standard' | 'deep'

export interface BBox {
  x0: number
  y0: number
  x1: number
  y1: number
}

export interface RenderCrop {
  data_uri: string | null
  none_reason: string | null
}

export interface Finding {
  id: string
  technique_id: string
  status: FindingStatus
  page: number | null
  bbox: BBox | null
  extracted_text: string
  render_crop: RenderCrop
  why_hidden: string
  mechanism: string
  reproduce: string
  severity: Severity
  severity_class: SeverityClass
  confidence: number
  views: string[]
  stage: number
  atr_rule: string | null
  extractor: string
}

export interface ParseFailure {
  parser: string
  reason: string
  message: string
  stage: number
  technique_id: string
}

export type RunStatus = 'visible' | 'hidden' | 'benign-hidden' | 'unverified'

export interface RunView {
  text: string
  bbox: BBox | null
  status: RunStatus
  finding_id: string | null
}

export interface PageView {
  number: number
  width_pt: number | null
  height_pt: number | null
  thumbnail: RenderCrop
  runs: RunView[]
}

export interface Report {
  schema_version: number
  tool_version: string
  rule_versions: Record<string, string>
  input_sha256: string
  input_type: string
  extractor: string
  tier: Tier
  profile: string
  page_count: number
  pages_render_verified: number
  dpi: number | null
  verdict: Verdict
  severity_counts: Record<Severity, number>
  findings: Finding[]
  /** Empty in a schema v1 report (before US-043). */
  pages?: PageView[]
  parse_failures: ParseFailure[]
  network_used: string[]
  timing_ms: Record<string, number>
}

export interface ScanSummary {
  id: string
  created_at: string
  expires_at: string
  file_name: string
  input_type: string
  verdict: Verdict
  tier: Tier
  profile: string
  tool_version: string
}

export interface FingerprintVerdict {
  extractor: string
  version: string
  returns_hidden_text: boolean | null
  agreement: number
}

export interface FingerprintRow {
  finding_id: string
  technique_id: string
  page: number | null
  text_preview: string
  extractors: FingerprintVerdict[]
}

export interface Fingerprint {
  input_sha256: string
  input_type: string
  default_extractor: string
  extractors: Record<string, string>
  failed: Record<string, string>
  rows: FingerprintRow[]
}

export interface ScanDetail extends ScanSummary {
  report: Report
  fingerprint: Fingerprint | null
}

export interface ScanList {
  scans: ScanSummary[]
}

export interface Technique {
  id: string
  formats: string[]
  views: string[]
  stage: number
  self_proving: boolean
  severity_class: string
  explanation: string
  threshold: string
  atr_rule: string | null
  rule_version: string
  release: string
}

export interface TechniqueList {
  techniques: Technique[]
}

export interface Profile {
  name: string
  version: string
  description: string
}

export interface ProfileList {
  profiles: Profile[]
}

export interface Health {
  status: string
  database: string
  version: string
}

/** The error body every backend error uses: { "error": { "code", "message", "details"? } }. */
export interface ErrorBody {
  error: {
    code: string
    message: string
    details?: unknown
  }
}
