import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createAnalysisTarget,
  deleteAnalysisTarget,
  getAnalysisTarget,
  getIngestionRun,
  getTargetSummary,
  listAnalysisTargets,
  listTargetReviews,
  renameAnalysisTarget,
  startFileImport,
  startUrlIngestion,
} from '@/lib/api/analysisTargets'
import { ApiError } from '@/lib/api/client'
import { isTerminal } from '@/lib/api/types'
import { useApiToken } from '@/hooks/useApiToken'

export const analysisKeys = {
  all: ['analysis-targets'] as const,
  detail: (id: string) => ['analysis-targets', id] as const,
  summary: (id: string) => ['analysis-targets', id, 'summary'] as const,
  reviews: (id: string, offset: number) =>
    ['analysis-targets', id, 'reviews', offset] as const,
  run: (runId: string) => ['ingestion-runs', runId] as const,
}

/** A denied or missing resource is a settled answer, so do not retry it. */
function retryUnlessClientError(failureCount: number, error: unknown) {
  if (error instanceof ApiError && error.status < 500) return false
  return failureCount < 2
}

export function useAnalysisTargets() {
  const getToken = useApiToken()
  return useQuery({
    queryKey: analysisKeys.all,
    queryFn: ({ signal }) => listAnalysisTargets(getToken, signal),
    retry: retryUnlessClientError,
  })
}

export function useAnalysisTarget(id: string | undefined) {
  const getToken = useApiToken()
  return useQuery({
    queryKey: analysisKeys.detail(id ?? ''),
    queryFn: ({ signal }) => getAnalysisTarget(id!, getToken, signal),
    enabled: Boolean(id),
    retry: retryUnlessClientError,
  })
}

export function useTargetSummary(id: string | undefined) {
  const getToken = useApiToken()
  return useQuery({
    queryKey: analysisKeys.summary(id ?? ''),
    queryFn: ({ signal }) => getTargetSummary(id!, getToken, signal),
    enabled: Boolean(id),
    retry: retryUnlessClientError,
  })
}

export function useTargetReviews(id: string | undefined, limit = 5, offset = 0) {
  const getToken = useApiToken()
  return useQuery({
    queryKey: analysisKeys.reviews(id ?? '', offset),
    queryFn: ({ signal }) => listTargetReviews(id!, { limit, offset }, getToken, signal),
    enabled: Boolean(id),
    retry: retryUnlessClientError,
  })
}

/** Polls while the run is in flight, then stops once it reaches a terminal state. */
export function useIngestionRun(runId: string | undefined) {
  const getToken = useApiToken()
  return useQuery({
    queryKey: analysisKeys.run(runId ?? ''),
    queryFn: ({ signal }) => getIngestionRun(runId!, getToken, signal),
    enabled: Boolean(runId),
    retry: retryUnlessClientError,
    refetchInterval: (query) => (isTerminal(query.state.data?.status) ? false : 2000),
  })
}

export function useCreateAnalysisTarget() {
  const getToken = useApiToken()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: { name: string; source_url: string }) =>
      createAnalysisTarget(input, getToken),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: analysisKeys.all }),
  })
}

export function useRenameAnalysisTarget() {
  const getToken = useApiToken()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) =>
      renameAnalysisTarget(id, name, getToken),
    onSuccess: (target) => {
      queryClient.invalidateQueries({ queryKey: analysisKeys.all })
      queryClient.invalidateQueries({ queryKey: analysisKeys.detail(target.id) })
    },
  })
}

export function useDeleteAnalysisTarget() {
  const getToken = useApiToken()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteAnalysisTarget(id, getToken),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: analysisKeys.all }),
  })
}

export function useStartIngestion(targetId: string | undefined) {
  const getToken = useApiToken()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (file?: File) =>
      file ? startFileImport(targetId!, file, getToken) : startUrlIngestion(targetId!, getToken),
    onSuccess: () => {
      if (!targetId) return
      queryClient.invalidateQueries({ queryKey: analysisKeys.summary(targetId) })
    },
  })
}
