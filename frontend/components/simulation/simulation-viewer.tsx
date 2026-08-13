'use client'

import { Canvas } from '@react-three/fiber'
import type { SimulationScreenplay } from '../../types/simulation'
import { useSimulationClock } from '../../hooks/useSimulationClock'
import SimulationControls from './controls'
import SimulationScene from './scene'
import { useMemo, useState } from 'react'

export default function SimulationViewer({ screenplay }: { screenplay: SimulationScreenplay }) {
  const clock = useSimulationClock(screenplay.duration_seconds)
  const [inspectMode, setInspectMode] = useState(false)
  const play = () => { setInspectMode(false); clock.play() }
  const restart = () => { setInspectMode(false); clock.restart() }
  const seek = (time: number) => { setInspectMode(false); clock.seek(time) }
  const currentEvent = useMemo(() => [...screenplay.events].sort((a, b) => a.time - b.time).filter((event) => event.time <= clock.currentTime).at(-1), [screenplay.events, clock.currentTime])
  return <section className="overflow-hidden rounded-2xl border border-slate-700/80 bg-slate-900 shadow-2xl shadow-black/40">
    <div className="relative h-[clamp(430px,66vh,680px)] bg-slate-950">
      <Canvas dpr={[1, 1.5]} shadows camera={{ position: [12, 12, 20], fov: 45 }}><SimulationScene screenplay={screenplay} currentTime={clock.currentTime} inspectMode={inspectMode} /></Canvas>
      <div className="pointer-events-none absolute left-4 top-4 rounded-md border border-white/10 bg-black/45 px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-slate-300 backdrop-blur-md">
        {inspectMode ? 'Inspect mode' : clock.isPlaying ? 'Cinematic playback' : 'Playback paused'}
      </div>
    </div>
    <div className="border-t border-slate-700/80 bg-slate-950/95 p-4 sm:p-5">
      <SimulationControls {...clock} play={play} restart={restart} seek={seek} events={screenplay.events} currentEventId={currentEvent?.id} inspectMode={inspectMode} toggleInspect={() => setInspectMode((value) => !value)} />
      <div className="mt-4 flex min-h-[58px] flex-col justify-between gap-3 border-t border-slate-800 pt-4 sm:flex-row sm:items-center">
        {currentEvent ? <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className={`rounded border px-1.5 py-0.5 text-[9px] font-bold tracking-wider ${currentEvent.certainty === 'supported' ? 'border-cyan-500/30 bg-cyan-950/30 text-cyan-300' : 'border-amber-500/25 bg-amber-950/20 text-amber-300'}`}>{currentEvent.certainty.toUpperCase()}</span>
            <p className="truncate text-sm font-medium text-slate-100">{currentEvent.label}</p>
          </div>
          <p className="mt-1 truncate font-mono text-[10px] text-slate-500">Evidence: {currentEvent.evidence_ids.join(', ') || 'none'} · Timeline: {currentEvent.timeline_event_ids.join(', ') || 'none'}</p>
        </div> : <p className="text-sm text-slate-500">No screenplay event at this time.</p>}
        <p className="max-w-xl text-[11px] leading-relaxed text-slate-500 sm:text-right">This reconstruction visualizes the selected theory based on available evidence. Inferred elements are shown separately.</p>
      </div>
    </div>
  </section>
}
