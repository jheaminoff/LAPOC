import { useState, useEffect, useCallback } from 'react'
import type { SpeechToken } from '@/types/speech'

interface UseSpeechTokenResult extends SpeechToken {
  loading: boolean
  error: string | null
}

const REFRESH_INTERVAL_MS = 9 * 60 * 1000

export function useSpeechToken(): UseSpeechTokenResult {
  const [token, setToken] = useState('')
  const [region, setRegion] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchToken = useCallback(async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/speech-token`)
      if (!res.ok) throw new Error(`Token fetch failed: ${res.status}`)
      const data: SpeechToken = await res.json()
      setToken(data.token)
      setRegion(data.region)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchToken()
    const interval = setInterval(fetchToken, REFRESH_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [fetchToken])

  return { token, region, loading, error }
}
