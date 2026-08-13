'use client'

import Link from 'next/link'
import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import SimulationViewer from '../../../components/simulation/simulation-viewer'
import { getSimulationScreenplay } from '../../../services/simulations'
import type { SimulationScreenplay } from '../../../types/simulation'

export default function SimulationPage() {
  const params = useParams<{ id: string }>()
  const [screenplay, setScreenplay] = useState<SimulationScreenplay | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [attempt, setAttempt] = useState(0)

  const load = useCallback(() => {
    setError(null)
    setScreenplay(null)
    getSimulationScreenplay(params.id).then(setScreenplay).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : 'Unable to load this simulation.')
    })
  }, [params.id])

  useEffect(load, [load, attempt])

  return <main className="min-h-screen overflow-x-hidden bg-[#080b10] text-slate-100">
    <header className="border-b border-white/10 bg-[#0b0f15]/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1500px] items-center gap-4 px-4 py-3 sm:px-7">
        <Link href={screenplay ? `/investigations/${screenplay.investigation_id}` : '/dashboard'} className="rounded-md border border-slate-700 px-2.5 py-1.5 text-xs text-slate-300 transition hover:bg-slate-800">← Back</Link>
        <div className="min-w-0">
          <p className="font-mono text-[9px] uppercase tracking-[0.22em] text-cyan-400">KHOJ Reconstruction</p>
          <h1 className="truncate text-sm font-semibold text-slate-100 sm:text-base">{screenplay?.title || 'Loading reconstruction'}</h1>
        </div>
        <span className="ml-auto hidden rounded-full border border-slate-700 bg-slate-900 px-2.5 py-1 font-mono text-[9px] uppercase tracking-wider text-slate-400 sm:block">Selected theory visualization</span>
      </div>
    </header>
    <div className="mx-auto max-w-[1500px] p-3 sm:p-5 lg:p-6">
      {error ? <section className="grid min-h-[70vh] place-items-center rounded-2xl border border-slate-800 bg-slate-950 p-6 text-center">
        <div><p className="text-base font-semibold text-slate-200">Reconstruction unavailable</p><p className="mt-2 max-w-lg text-sm text-slate-500">{error}</p><button onClick={() => setAttempt((value) => value + 1)} className="mt-5 rounded-md border border-cyan-500/30 bg-cyan-950/20 px-4 py-2 text-sm text-cyan-200 hover:bg-cyan-950/40">Try again</button></div>
      </section> : screenplay ? <SimulationViewer screenplay={screenplay} /> : <section className="grid min-h-[70vh] place-items-center rounded-2xl border border-slate-800 bg-slate-950 text-sm text-slate-400">Loading simulation…</section>}
    </div>
  </main>
}
