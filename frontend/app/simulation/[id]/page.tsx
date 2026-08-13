'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import SimulationViewer from '../../../components/simulation/simulation-viewer'
import { getSimulationScreenplay } from '../../../services/simulations'
import type { SimulationScreenplay } from '../../../types/simulation'

export default function SimulationPage() {
  const params = useParams<{ id: string }>()
  const [screenplay, setScreenplay] = useState<SimulationScreenplay | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { getSimulationScreenplay(params.id).then(setScreenplay).catch(() => setError('Unable to load this simulation.')) }, [params.id])
  if (error) return <main className="grid min-h-screen place-items-center bg-slate-950 p-6 text-slate-200">{error}</main>
  if (!screenplay) return <main className="grid min-h-screen place-items-center bg-slate-950 text-slate-300">Loading simulation…</main>
  return <main className="min-h-screen bg-slate-950 p-4 text-slate-100 sm:p-8"><div className="mx-auto max-w-6xl"><p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">KHOJ Reconstruction</p><h1 className="mb-6 text-2xl font-semibold sm:text-3xl">{screenplay.title}</h1><SimulationViewer screenplay={screenplay} /></div></main>
}
