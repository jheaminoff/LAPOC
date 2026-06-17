import { useState, useRef, useCallback, useEffect } from 'react'
import type { VisemeEvent } from '@/types/speech'

interface UseVisemeSchedulerResult {
  scheduleViseme: (id: number, offsetMs: number) => void
  currentVisemeId: number
  clearQueue: () => void
  startPlayback: () => void
}

export function useVisemeScheduler(): UseVisemeSchedulerResult {
  const [currentVisemeId, setCurrentVisemeId] = useState(0)
  const queueRef = useRef<VisemeEvent[]>([])
  const startTimeRef = useRef<number>(0)
  const rafRef = useRef<number>(0)
  const tickRef = useRef<(() => void) | null>(null)

  const tick = useCallback(() => {
    const elapsed = Date.now() - startTimeRef.current
    const queue = queueRef.current

    while (queue.length > 0 && queue[0].audioOffsetMs <= elapsed) {
      const event = queue.shift()!
      setCurrentVisemeId(event.visemeId)
    }

    if (queue.length > 0) {
      const fn = tickRef.current
      if (fn) rafRef.current = requestAnimationFrame(fn)
    } else {
      setCurrentVisemeId(0)
    }
  }, [])

  useEffect(() => {
    tickRef.current = tick
  }, [tick])

  const startPlayback = useCallback(() => {
    startTimeRef.current = Date.now()
    cancelAnimationFrame(rafRef.current)
    const fn = tickRef.current
    if (fn) rafRef.current = requestAnimationFrame(fn)
  }, [tickRef])

  const scheduleViseme = useCallback((id: number, offsetMs: number) => {
    queueRef.current.push({ visemeId: id, audioOffsetMs: offsetMs })
    queueRef.current.sort((a, b) => a.audioOffsetMs - b.audioOffsetMs)
  }, [])

  const clearQueue = useCallback(() => {
    queueRef.current = []
    cancelAnimationFrame(rafRef.current)
    setCurrentVisemeId(0)
  }, [])

  return { scheduleViseme, currentVisemeId, clearQueue, startPlayback }
}
