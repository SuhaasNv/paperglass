import { NavLink, Outlet } from 'react-router'

/**
 * The frame every page sits in. Plumbing: a heading, the navigation and the outlet. The
 * design pass owns the markup and the styles.
 */
export function Layout() {
  return (
    <>
      <header>
        <p>Paperglass</p>
        <nav aria-label="Main">
          <ul>
            <li>
              <NavLink to="/">Upload</NavLink>
            </li>
            <li>
              <NavLink to="/history">History</NavLink>
            </li>
            <li>
              <NavLink to="/techniques">Techniques</NavLink>
            </li>
            <li>
              <NavLink to="/about">About</NavLink>
            </li>
          </ul>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </>
  )
}
