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

const WAV_MIME = 'audio/wav; codecs="1"'

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
  const mediaSourceRef = useRef<MediaSource | null>(null)
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
    speechConfig.speechSynthesisOutputFormat = SpeechSDK.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm

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

    // ── MediaSource streaming setup ──
    const chunks: ArrayBuffer[] = []
    const mediaSource = new MediaSource()
    mediaSourceRef.current = mediaSource
    let sourceBuffer: SourceBuffer | null = null
    let appendQueue: ArrayBuffer[] = []
    let isAppending = false

    const tryAppend = () => {
      if (!sourceBuffer || isAppending || appendQueue.length === 0) return
      isAppending = true
      const chunk = appendQueue.shift()!
      try {
        sourceBuffer.appendBuffer(chunk)
      } catch (e) {
        console.error('[TTS] SourceBuffer.appendBuffer error:', e)
        isAppending = false
      }
    }

    mediaSource.onsourceopen = () => {
      try {
        sourceBuffer = mediaSource.addSourceBuffer(WAV_MIME)
        sourceBuffer.onupdateend = () => {
          isAppending = false
          tryAppend()
        }
        tryAppend()
      } catch (e) {
        console.error('[TTS] addSourceBuffer error:', e)
        // Fallback: play chunks after full synthesis
        mediaSourceRef.current = null
      }
    }

    const audioUrl = URL.createObjectURL(mediaSource)
    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current)
    }
    blobUrlRef.current = audioUrl

    if (!audioRef.current) {
      audioRef.current = new Audio()
    }
    const audio = audioRef.current
    audio.src = audioUrl
    audio.onended = () => {
      setIsSpeaking(false)
    }
    audio.onerror = () => {
      console.warn('[TTS] Audio playback error — trying fallback')
      setIsSpeaking(false)
    }
    audio.play().catch((err) => {
      console.warn('[TTS] Audio play failed:', err)
      setIsSpeaking(false)
    })

    // ── Stream chunks via synthesizing event ──
    synth.synthesizing = (_s, e) => {
      const data = e.result.audioData
      if (!data?.byteLength) return
      const copy = data.slice(0)
      chunks.push(copy)
      appendQueue.push(copy)
      if (mediaSource.readyState === 'open') {
        tryAppend()
      }
    }

    synth.synthesisCompleted = () => {
      if (mediaSource.readyState === 'open') {
        try {
          mediaSource.endOfStream()
        } catch {
          // already ended
        }
      }
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
      (_result) => {
        synth.close()
        synthRef.current = null
        // Ensure stream ended even if synthesisCompleted missed
        if (mediaSourceRef.current?.readyState === 'open') {
          try {
            mediaSourceRef.current.endOfStream()
          } catch {
            // already ended
          }
        }
        // Fallback: if MediaSource didn't work, try non-streaming
        if (audio.paused && chunks.length > 0) {
          setIsSpeaking(false)
        }
      },
      (err) => {
        console.error('[TTS] speakSsmlAsync error:', err)
        setIsSpeaking(false)
        synth.close()
        synthRef.current = null
        if (mediaSourceRef.current?.readyState === 'open') {
          try {
            mediaSourceRef.current.endOfStream('network')
          } catch {
            // already ended
          }
        }
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
