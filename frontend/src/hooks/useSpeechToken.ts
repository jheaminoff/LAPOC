import { useReducer, useEffect, useCallback } from 'react'
import type { SpeechToken } from '@/types/speech'

interface UseSpeechTokenResult extends SpeechToken {
  loading: boolean
  error: string | null
}

interface State {
  token: string
  region: string
  loading: boolean
  error: string | null
}

type Action =
  | { type: 'success'; token: string; region: string }
  | { type: 'error'; error: string }
  | { type: 'done' }

const INITIAL: State = {
  token: '',
  region: '',
  loading: true,
  error: null,
}

function reducer(_state: State, action: Action): State {
  switch (action.type) {
    case 'success':
      return { token: action.token, region: action.region, loading: false, error: null }
    case 'error':
      return { token: '', region: '', loading: false, error: action.error }
    case 'done':
      return { token: '', region: '', loading: false, error: null }
  }
}

const REFRESH_INTERVAL_MS = 9 * 60 * 1000

export function useSpeechToken(): UseSpeechTokenResult {
  const [{ token, region, loading, error }, dispatch] = useReducer(reducer, INITIAL)

  const fetchToken = useCallback(async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/speech-token`)
      if (!res.ok) throw new Error(`Token fetch failed: ${res.status}`)
      const data = await res.json() as SpeechToken
      dispatch({ type: 'success', token: data.token, region: data.region })
    } catch (err) {
      dispatch({ type: 'error', error: err instanceof Error ? err.message : 'Unknown error' })
    }
  }, [])

  useEffect(() => {
    void fetchToken()
    const interval = setInterval(fetchToken, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [fetchToken])

  return { token, region, loading, error }
}
