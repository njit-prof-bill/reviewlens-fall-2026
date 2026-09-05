import { useAuth } from '@clerk/clerk-react'
import { useCallback } from 'react'

/** Clerk token getter shaped for the API client. */
export function useApiToken() {
  const { getToken } = useAuth()
  return useCallback(() => getToken({ skipCache: true }), [getToken])
}
