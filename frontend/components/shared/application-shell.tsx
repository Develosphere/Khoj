'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, type ReactNode } from 'react'

type NavigationItem = {
  href: string
  label: string
  description: string
  icon: ReactNode
}

const navigation: NavigationItem[] = [
  {
    href: '/dashboard',
    label: 'Case Board',
    description: 'Investigations overview',
    icon: <path d="M4 7.5h16M7 4h10l1 3.5H6L7 4Zm-1 3.5h12v11H6v-11Zm4 3.5h4" />,
  },
  {
    href: '/scrapers',
    label: 'Source Desk',
    description: 'Source collection',
    icon: <><circle cx="11" cy="11" r="5.5" /><path d="m15.2 15.2 4 4" /></>,
  },
]

function pageContext(pathname: string) {
  if (pathname.startsWith('/investigations/')) return { eyebrow: 'Case dossier', title: 'Investigation workspace' }
  if (pathname === '/scrapers') return { eyebrow: 'Collection desk', title: 'Source intelligence' }
  return { eyebrow: 'Investigation system', title: 'Case board' }
}

function Brand() {
  return <Link href="/dashboard" className="group flex items-center gap-3 rounded-md p-1 focus-visible:outline-none">
    <span className="grid h-8 w-8 place-items-center rounded border border-crimson/50 bg-noir-800 font-mono text-sm font-bold text-crimson-bright shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">K</span>
    <span className="min-w-0">
      <span className="block font-sans text-sm font-bold tracking-[0.18em] text-zinc-100">KHOJ</span>
      <span className="block font-mono text-[8px] uppercase tracking-[0.16em] text-zinc-500">Investigation system</span>
    </span>
  </Link>
}

function NavItems({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  return <nav aria-label="Primary navigation" className="space-y-1">
    <p className="metadata-label px-3 pb-2 pt-1">Workspace</p>
    {navigation.map((item) => {
      const active = pathname === item.href || (item.href === '/dashboard' && pathname.startsWith('/investigations/'))
      return <Link key={item.href} href={item.href} onClick={onNavigate} aria-current={active ? 'page' : undefined} className={`group relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors ${active ? 'bg-noir-800 text-zinc-100' : 'text-zinc-400 hover:bg-noir-800/70 hover:text-zinc-100'}`}>
        <span aria-hidden="true" className={`absolute bottom-2 left-0 top-2 w-0.5 rounded-r ${active ? 'bg-crimson' : 'bg-transparent group-hover:bg-zinc-600'}`} />
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" className={`h-4 w-4 shrink-0 ${active ? 'text-crimson-bright' : 'text-zinc-500 group-hover:text-zinc-300'}`}>{item.icon}</svg>
        <span className="min-w-0"><span className="block font-medium">{item.label}</span><span className="block text-[10px] text-zinc-600 group-hover:text-zinc-500">{item.description}</span></span>
      </Link>
    })}
  </nav>
}

export default function ApplicationShell({ children }: { children: ReactNode }) {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)
  const excluded = pathname === '/' || pathname.startsWith('/login') || pathname.startsWith('/signup') || pathname.startsWith('/verify-2fa') || pathname.startsWith('/simulation/')

  if (excluded) return <>{children}</>

  const context = pageContext(pathname)
  return <div className="app-shell">
    <aside className="app-sidebar hidden lg:flex">
      <div className="border-b border-noir-700 px-5 py-5"><Brand /></div>
      <div className="flex-1 px-3 py-5"><NavItems pathname={pathname} /></div>
      <div className="border-t border-noir-700 px-5 py-4"><p className="metadata-label">Secure workspace</p><p className="mt-1 font-mono text-[10px] text-zinc-500">KHOJ / ACTIVE</p></div>
    </aside>

    <div className="app-frame">
      <header className="app-header">
        <div className="flex min-w-0 items-center gap-3">
          <button type="button" onClick={() => setMobileOpen(true)} className="inline-grid h-9 w-9 place-items-center rounded border border-noir-700 text-zinc-300 hover:bg-noir-800 lg:hidden" aria-label="Open navigation">
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4"><path d="M4 7h16M4 12h16M4 17h16" /></svg>
          </button>
          <div className="min-w-0"><p className="metadata-label text-zinc-500">{context.eyebrow}</p><p className="truncate text-sm font-semibold text-zinc-200">{context.title}</p></div>
        </div>
        <div className="hidden items-center gap-2 sm:flex"><span className="h-1.5 w-1.5 rounded-full bg-caution" aria-hidden="true" /><span className="font-mono text-[10px] uppercase tracking-wider text-zinc-500">Authenticated workspace</span></div>
      </header>

      <main className="app-content">{children}</main>
    </div>

    {mobileOpen && <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu">
      <button type="button" className="absolute inset-0 bg-black/70" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />
      <aside className="relative flex h-full w-[min(18rem,calc(100vw-3rem))] flex-col border-r border-noir-700 bg-noir-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-noir-700 px-4 py-4"><Brand /><button type="button" onClick={() => setMobileOpen(false)} className="grid h-8 w-8 place-items-center rounded text-zinc-400 hover:bg-noir-800 hover:text-zinc-100" aria-label="Close navigation">×</button></div>
        <div className="flex-1 px-3 py-5"><NavItems pathname={pathname} onNavigate={() => setMobileOpen(false)} /></div>
      </aside>
    </div>}
  </div>
}
