'use client'

import { Canvas } from '@react-three/fiber'
import type { SimulationScreenplay } from '../../types/simulation'
import { useSimulationClock } from '../../hooks/useSimulationClock'
import SimulationControls from './controls'
import SimulationScene from './scene'

export default function SimulationViewer({ screenplay }: { screenplay: SimulationScreenplay }) {
  const clock = useSimulationClock(screenplay.duration_seconds)
  return <section className="overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
    <div className="h-[62vh] min-h-[420px] bg-slate-950"><Canvas shadows camera={{ position: [12, 12, 20], fov: 45 }}><SimulationScene screenplay={screenplay} currentTime={clock.currentTime} /></Canvas></div>
    <div className="border-t border-slate-700 p-4"><SimulationControls {...clock} /></div>
  </section>
}
