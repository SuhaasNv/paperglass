/** TanStack Query hooks over the client. Keys live here so pages never spell them. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createScan,
  fingerprintScan,
  getScan,
  listProfiles,
  listScans,
  listTechniques,
  type CreateScanInput,
} from './client'
import type { ScanDetail } from './types'

export const keys = {
  scans: ['scans'] as const,
  scan: (id: string) => ['scans', id] as const,
  techniques: ['techniques'] as const,
  profiles: ['profiles'] as const,
}

export function useScan(id: string) {
  // A report never changes once written, so a fresh one (from the upload) is not fetched again.
  return useQuery({
    queryKey: keys.scan(id),
    queryFn: () => getScan(id),
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}

export function useScans() {
  return useQuery({ queryKey: keys.scans, queryFn: listScans, retry: false })
}

export function useTechniques() {
  return useQuery({ queryKey: keys.techniques, queryFn: listTechniques, staleTime: Infinity })
}

export function useProfiles() {
  return useQuery({ queryKey: keys.profiles, queryFn: listProfiles, staleTime: Infinity })
}

export function useCreateScan() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (input: CreateScanInput) => createScan(input),
    onSuccess: (scan: ScanDetail) => {
      client.setQueryData(keys.scan(scan.id), scan)
      void client.invalidateQueries({ queryKey: keys.scans, exact: true })
    },
  })
}

export function useFingerprintScan(id: string) {
  const client = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => fingerprintScan(id, file),
    onSuccess: (scan: ScanDetail) => {
      client.setQueryData(keys.scan(scan.id), scan)
    },
  })
}
