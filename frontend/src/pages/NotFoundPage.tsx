import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <section aria-labelledby="notfound-heading">
      <h1 id="notfound-heading">Not found</h1>
      <p>
        There is nothing at this address. <Link to="/">Scan a document</Link>.
      </p>
    </section>
  )
}
