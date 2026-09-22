import { ApiError } from '../api/client'

/** One sentence a person can act on. Never a stack trace, never a raw status code alone. */
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return 'This report does not exist or has expired.'
    if (error.status === 413) return error.message
    if (error.status === 0) return error.message
    return error.message
  }
  if (error instanceof Error) return error.message
  return 'Something went wrong.'
}
