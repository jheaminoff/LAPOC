import { useState, useRef, useCallback, useEffect } from 'react'
import * as SpeechSDK from 'microsoft-cognitiveservices-speech-sdk'

const CONNECT_TIMEOUT_MS = 10_000

interface UseSpeechRecognizerInput {
  token: string
  region: string
  language?: string
  onResult: (text: string) => void
}

interface UseSpeechRecognizerResult {
  isListening: boolean
  isConnecting: boolean
  isMuted: boolean
  interimTranscript: string
  startListening: () => void
  stopListening: () => void
  mute: () => void
  unmute: () => void
}

export function useSpeechRecognizer({
  token,
  region,
  language = 'en-US',
  onResult,
}: UseSpeechRecognizerInput): UseSpeechRecognizerResult {
  const [isListening, setIsListening] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  const recognizerRef = useRef<SpeechSDK.SpeechRecognizer | null>(null)
  const activeRef = useRef(false)
  const mutedRef = useRef(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const clearConnectTimeout = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
  }, [])

  const buildAndStart = useCallback(() => {
    if (!token || !region) {
      console.warn('[STT] Aborting — missing token or region')
      setIsConnecting(false)
      return
    }
    console.log('[STT] Connecting with region:', region)
    setIsConnecting(true)

    // Connection timeout guard
    clearConnectTimeout()
    timeoutRef.current = setTimeout(() => {
      if (!activeRef.current) return
      console.warn('[STT] Connection timed out after 10s — stopping and retrying')
      const rec = recognizerRef.current
      if (rec) {
        rec.close()
        recognizerRef.current = null
      }
      activeRef.current = false
      setIsConnecting(false)
      setIsListening(false)
      // Auto-retry once
      activeRef.current = true
      buildAndStart()
    }, CONNECT_TIMEOUT_MS)

    const speechConfig = SpeechSDK.SpeechConfig.fromAuthorizationToken(token, region)
    speechConfig.speechRecognitionLanguage = language
    const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput()
    const recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig)
    recognizerRef.current = recognizer

    recognizer.recognizing = (_s, e) => {
      if (mutedRef.current) return
      setInterimTranscript(e.result.text)
    }

    recognizer.recognized = (_s, e) => {
      setInterimTranscript('')
      if (mutedRef.current) return
      if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech && e.result.text.trim()) {
        onResult(e.result.text)
      }
    }

    recognizer.canceled = (_s, e) => {
      console.error('[STT] Canceled —', e.errorDetails || e.reason)
      clearConnectTimeout()
      activeRef.current = false
      setIsConnecting(false)
      setIsListening(false)
    }

    recognizer.sessionStarted = () => {
      console.log('[STT] Session started')
      clearConnectTimeout()
      setIsConnecting(false)
      setIsListening(true)
    }

    recognizer.sessionStopped = () => {
      console.log('[STT] Session stopped')
      clearConnectTimeout()
      activeRef.current = false
      setIsConnecting(false)
      setIsListening(false)
      recognizerRef.current?.close()
      recognizerRef.current = null
    }

    recognizer.startContinuousRecognitionAsync(
      () => console.log('[STT] Continuous recognition started'),
      (err) => {
        console.error('[STT] startContinuousRecognitionAsync error:', err)
        clearConnectTimeout()
        activeRef.current = false
        setIsConnecting(false)
        setIsListening(false)
      }
    )
  }, [token, region, language, onResult, clearConnectTimeout])

  const startListening = useCallback(() => {
    if (activeRef.current) {
      console.log('[STT] Already active — skipping')
      return
    }
    activeRef.current = true
    buildAndStart()
  }, [buildAndStart])

  const stopListening = useCallback(() => {
    activeRef.current = false
    mutedRef.current = false
    setIsMuted(false)
    clearConnectTimeout()
    const rec = recognizerRef.current
    if (!rec) return
    rec.stopContinuousRecognitionAsync(
      () => {
        setIsListening(false)
        rec.close()
        recognizerRef.current = null
      },
      (err) => console.error('[STT] stop error:', err)
    )
  }, [clearConnectTimeout])

  const mute = useCallback(() => {
    mutedRef.current = true
    setIsMuted(true)
    setInterimTranscript('')
  }, [])

  const unmute = useCallback(() => {
    mutedRef.current = false
    setIsMuted(false)
  }, [])

  useEffect(() => {
    return () => {
      clearConnectTimeout()
      activeRef.current = false
      recognizerRef.current?.close()
    }
  }, [clearConnectTimeout])

  return { isListening, isConnecting, isMuted, interimTranscript, startListening, stopListening, mute, unmute }
}
