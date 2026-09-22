import { NavLink, Outlet, useLocation } from 'react-router'
import { useEffect, useRef } from 'react'

import { BrandMark } from '../components/BrandMark'
import { Grain } from '../components/Grain'
import { useReveal, useScrollProgress } from '../hooks/useReveal'

const NAV: Array<[string, string]> = [
  ['Scan', '/scan'],
  ['History', '/history'],
  ['Techniques', '/techniques'],
  ['About', '/about'],
]

/**
 * The frame every page sits in: header with the drawn rule, the scroll progress hairline, the
 * grain, the outlet, the footer. Reveals are observed from here so pages only mark elements.
 */
export function Layout() {
  const main = useRef<HTMLElement>(null)
  const location = useLocation()
  useScrollProgress()
  useReveal(main)
  useEffect(() => {
    if (!location.hash) window.scrollTo({ top: 0 })
  }, [location.pathname, location.hash])

  return (
    <>
      <Grain />
      <div className="progress" aria-hidden="true" />
      <header className="relative z-30 flex h-16 items-center justify-between border-b border-rule px-5 md:px-14">
        <div className="rule-draw absolute right-0 bottom-[-1px] left-0 h-px bg-ink" aria-hidden="true" />
        <NavLink to="/" className="flex items-center gap-2.5 text-[12px] font-semibold tracking-[0.16em] text-ink no-underline">
          <BrandMark size={20} />
          PAPERGLASS
        </NavLink>
        <nav aria-label="Main" className="hidden gap-7 text-[14px] font-medium md:flex">
          {NAV.map(([label, to]) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `border-b pb-[3px] no-underline ${isActive ? 'border-glass text-ink' : 'border-transparent text-ink-2'}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <a
          href="https://github.com/SuhaasNv/paperglass"
          className="hidden text-[12px] tracking-[0.04em] text-ink-2 no-underline md:block"
        >
          Apache-2.0 · GitHub
        </a>
        <nav aria-label="Main, compact" className="flex gap-4 text-[13px] font-medium md:hidden">
          {NAV.map(([label, to]) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `no-underline ${isActive ? 'text-ink' : 'text-ink-2'}`}
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main ref={main} key={location.pathname} className="relative z-10">
        <Outlet />
      </main>
      <footer className="relative z-10 flex flex-col gap-3 border-t border-ink px-5 py-6 text-[12px] tracking-[0.04em] text-ink-2 md:flex-row md:items-center md:justify-between md:px-14">
        <div className="flex items-center gap-2.5">
          <BrandMark size={16} className="text-ink" />
          <span className="font-semibold tracking-[0.16em] text-ink">PAPERGLASS</span>
          <span className="ital text-[15px] tracking-normal">see exactly what the model reads</span>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <NavLink to="/techniques" className="text-ink-2 no-underline">Techniques</NavLink>
          <NavLink to="/about" className="text-ink-2 no-underline">About</NavLink>
          <a href="https://github.com/SuhaasNv/paperglass" className="text-ink-2 no-underline">GitHub</a>
          <a href="https://github.com/SuhaasNv/paperglass/blob/main/SECURITY.md" className="text-ink-2 no-underline">Security</a>
          <span>No telemetry · files never stored</span>
        </div>
      </footer>
    </>
  )
}
