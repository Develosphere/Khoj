'use client'

import type { SimulationEvent } from '../../types/simulation'

type ControlsProps = { currentTime: number; duration: number; isPlaying: boolean; play: () => void; pause: () => void; restart: () => void; seek: (time: number) => void; events: SimulationEvent[]; currentEventId?: string; inspectMode: boolean; toggleInspect: () => void }
const formatTime = (time: number) => `${Math.floor(time / 60).toString().padStart(2, '0')}:${Math.floor(time % 60).toString().padStart(2, '0')}`

export default function SimulationControls({ currentTime, duration, isPlaying, play, pause, restart, seek, events, currentEventId, inspectMode, toggleInspect }: ControlsProps) {
  return <div className="flex flex-col gap-3 text-slate-100">
    <div className="flex items-center gap-2">
      <button className="rounded-md bg-cyan-500 px-3 py-1.5 text-sm font-semibold text-slate-950 hover:bg-cyan-300" onClick={isPlaying ? pause : play}>{isPlaying ? 'Pause' : 'Play'}</button>
      <button className="rounded-md border border-slate-600 px-3 py-1.5 text-sm font-medium hover:bg-slate-800" onClick={restart}>Restart</button>
      <button disabled={isPlaying} className={`rounded-md border px-3 py-1.5 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-40 ${inspectMode ? 'border-cyan-400 bg-cyan-950 text-cyan-200' : 'border-slate-600 hover:bg-slate-800'}`} onClick={toggleInspect}>{inspectMode ? 'Exit inspect' : 'Inspect'}</button>
      <span className="ml-auto font-mono text-sm text-slate-300">{formatTime(currentTime)} / {formatTime(duration)}</span>
    </div>
    <div className="relative px-1 pt-3"><input aria-label="Simulation timeline" className="block w-full cursor-pointer accent-cyan-400" type="range" min="0" max={duration} step="0.01" value={currentTime} onChange={(event) => seek(Number(event.target.value))} />
      {events.map((event) => <button key={event.id} title={`${formatTime(event.time)} — ${event.label}`} aria-label={`Seek to ${event.label}`} onClick={() => seek(event.time)} className={`absolute top-0 h-3.5 -translate-x-1/2 rounded-full transition-all ${event.id === currentEventId ? 'z-10 w-2 bg-white ring-2 ring-cyan-400/50' : event.certainty === 'inferred' ? 'w-1.5 bg-slate-500 hover:bg-slate-300' : 'w-1.5 bg-cyan-300 hover:bg-cyan-100'}`} style={{ left: `${Math.min(100, Math.max(0, (event.time / duration) * 100))}%` }} />)}
    </div>
  </div>
}
