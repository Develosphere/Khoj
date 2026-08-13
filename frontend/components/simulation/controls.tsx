'use client'

type ControlsProps = { currentTime: number; duration: number; isPlaying: boolean; play: () => void; pause: () => void; restart: () => void; seek: (time: number) => void }
const formatTime = (time: number) => `${Math.floor(time / 60).toString().padStart(2, '0')}:${Math.floor(time % 60).toString().padStart(2, '0')}`

export default function SimulationControls({ currentTime, duration, isPlaying, play, pause, restart, seek }: ControlsProps) {
  return <div className="flex flex-col gap-3 rounded-xl border border-slate-700 bg-slate-950/90 p-4 text-slate-100 shadow-xl backdrop-blur">
    <div className="flex items-center gap-2">
      <button className="rounded-md bg-cyan-500 px-3 py-1.5 text-sm font-semibold text-slate-950 hover:bg-cyan-300" onClick={isPlaying ? pause : play}>{isPlaying ? 'Pause' : 'Play'}</button>
      <button className="rounded-md border border-slate-600 px-3 py-1.5 text-sm font-medium hover:bg-slate-800" onClick={restart}>Restart</button>
      <span className="ml-auto font-mono text-sm text-slate-300">{formatTime(currentTime)} / {formatTime(duration)}</span>
    </div>
    <input aria-label="Simulation timeline" className="w-full accent-cyan-400" type="range" min="0" max={duration} step="0.01" value={currentTime} onChange={(event) => seek(Number(event.target.value))} />
  </div>
}
