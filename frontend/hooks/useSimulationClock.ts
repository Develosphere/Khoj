'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { clampSimulationTime } from '../lib/simulation-runtime'

export function useSimulationClock(duration: number) {
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const frameRef = useRef<number | null>(null)
  const lastFrameRef = useRef<number | null>(null)

  useEffect(() => {
    if (!isPlaying) return
    const tick = (now: number) => {
      const previous = lastFrameRef.current ?? now
      const delta = (now - previous) / 1000
      lastFrameRef.current = now
      setCurrentTime((time) => {
        const next = clampSimulationTime(time + delta, duration)
        if (next >= duration) setIsPlaying(false)
        return next
      })
      frameRef.current = requestAnimationFrame(tick)
    }
    frameRef.current = requestAnimationFrame(tick)
    return () => { if (frameRef.current !== null) cancelAnimationFrame(frameRef.current); lastFrameRef.current = null }
  }, [duration, isPlaying])

  const play = useCallback(() => { if (currentTime >= duration) setCurrentTime(0); setIsPlaying(true) }, [currentTime, duration])
  const pause = useCallback(() => setIsPlaying(false), [])
  const restart = useCallback(() => { setIsPlaying(false); setCurrentTime(0) }, [])
  const seek = useCallback((time: number) => setCurrentTime(clampSimulationTime(time, duration)), [duration])
  return { currentTime, duration, isPlaying, play, pause, restart, seek }
}
