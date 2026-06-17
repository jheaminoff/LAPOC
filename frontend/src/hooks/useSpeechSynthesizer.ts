import { useState, useRef, useCallback, useEffect } from 'react'
import * as SpeechSDK from 'microsoft-cognitiveservices-speech-sdk'

interface UseSpeechSynthesizerInput {
  token: string
  region: string
  language?: string
  onViseme?: (id: number, offsetMs: number) => void
}

const VOICE_MAP: Record<string, string> = {
  'en-US': 'en-US-JennyNeural',
}

interface UseSpeechSynthesizerResult {
  speak: (text: string) => void
  isSpeaking: boolean
  stop: () => void
  resumeAudio: () => void
}

export function useSpeechSynthesizer({
  token,
  region,
  language = 'en-US',
  onViseme,
}: UseSpeechSynthesizerInput): UseSpeechSynthesizerResult {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const synthRef = useRef<SpeechSDK.SpeechSynthesizer | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const blobUrlRef = useRef<string | null>(null)

  const resumeAudio = useCallback(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio()
      audioRef.current.autoplay = false
    }
    audioRef.current.src = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA='
    audioRef.current.play().catch(() => {})
  }, [])

  const buildSynthesizer = useCallback(() => {
    if (!token || !region) {
      console.warn('[TTS] Aborting — missing token or region')
      return null
    }

    const speechConfig = SpeechSDK.SpeechConfig.fromAuthorizationToken(token, region)
    speechConfig.speechSynthesisVoiceName = VOICE_MAP[language] ?? VOICE_MAP['en-US']
    // MP3 output: universally supported by all browsers (no MSE/WAV needed)
    speechConfig.speechSynthesisOutputFormat = SpeechSDK.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3

    const nullStream = SpeechSDK.AudioOutputStream.createPullStream()
    const audioConfig = SpeechSDK.AudioConfig.fromStreamOutput(nullStream)
    const synth = new SpeechSDK.SpeechSynthesizer(speechConfig, audioConfig)

    synth.visemeReceived = (_s, e) => {
      onViseme?.(e.visemeId, e.audioOffset / 10000)
    }
    synth.SynthesisCanceled = (_s, e) => console.error('[TTS] canceled:', e.result.errorDetails)

    return synth
  }, [token, region, language, onViseme])

  const speak = useCallback((text: string) => {
    const synth = buildSynthesizer()
    if (!synth) return
    synthRef.current?.close()
    synthRef.current = synth
    setIsSpeaking(true)

    if (!audioRef.current) {
      audioRef.current = new Audio()
    }
    const audio = audioRef.current

    // Collect MP3 chunks during synthesis
    const chunks: ArrayBuffer[] = []

    synth.synthesizing = (_s, e) => {
      const data = e.result.audioData
      if (data?.byteLength) chunks.push(data.slice(0))
    }

    synth.synthesisCompleted = () => {
      if (chunks.length === 0) {
        setIsSpeaking(false)
        return
      }

      // Revoke previous blob URL before creating a new one
      if (blobUrlRef.current) {
        URL.revokeObjectURL(blobUrlRef.current)
      }

      const blob = new Blob(chunks, { type: 'audio/mpeg' })
      const url = URL.createObjectURL(blob)
      blobUrlRef.current = url

      audio.src = url
      audio.onended = () => setIsSpeaking(false)
      audio.onerror = () => {
        console.warn('[TTS] Audio playback error')
        setIsSpeaking(false)
      }
      audio.play().catch((err) => {
        console.warn('[TTS] Audio play failed:', err)
        setIsSpeaking(false)
      })
    }

    // ── Kick off synthesis ──
    const escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;')
    const voice = VOICE_MAP[language] ?? VOICE_MAP['en-US']
    const ssml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="${language}"><voice name="${voice}">${escaped}</voice></speak>`

    synth.speakSsmlAsync(
      ssml,
      () => {
        synth.close()
        synthRef.current = null
      },
      (err) => {
        console.error('[TTS] speakSsmlAsync error:', err)
        setIsSpeaking(false)
        synth.close()
        synthRef.current = null
      },
    )
  }, [buildSynthesizer, language])

  const stop = useCallback(() => {
    const synth = synthRef.current
    synthRef.current = null
    if (synth) {
      const sdk = synth as SpeechSDK.SpeechSynthesizer & {
        stopSpeakingAsync?: (onSuccess: () => void, onError: () => void) => void
      }
      if (typeof sdk.stopSpeakingAsync === 'function') {
        sdk.stopSpeakingAsync(() => synth.close(), () => synth.close())
      } else {
        synth.close()
      }
    }
    const audio = audioRef.current
    if (audio && !audio.paused) {
      const startVol = audio.volume
      const step = startVol / 10
      let ticks = 0
      const fade = setInterval(() => {
        ticks++
        audio.volume = Math.max(0, startVol - step * ticks)
        if (ticks >= 10) {
          clearInterval(fade)
          audio.pause()
          audio.src = ''
          audio.volume = 1
        }
      }, 20)
    } else if (audio) {
      audio.pause()
      audio.src = ''
    }
    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current)
      blobUrlRef.current = null
    }
    setIsSpeaking(false)
  }, [])

  useEffect(() => {
    return () => {
      synthRef.current?.close()
      if (audioRef.current) {
        audioRef.current.pause()
      }
      if (blobUrlRef.current) {
        URL.revokeObjectURL(blobUrlRef.current)
      }
    }
  }, [])

  return { speak, isSpeaking, stop, resumeAudio }
}
