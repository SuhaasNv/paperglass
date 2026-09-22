import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <section aria-labelledby="notfound-heading" className="grid grid-cols-1 gap-6 px-5 py-16 md:grid-cols-12 md:items-center md:gap-x-6 md:px-14 md:py-20">
      <span className="ital rise d1 text-[80px] leading-none text-ink-2 md:col-span-2 md:text-[120px]">404</span>
      <div className="flex flex-col gap-4 border-l border-ink pl-6 md:col-span-8 md:pl-8">
        <h1 id="notfound-heading" className="rise d2 text-[44px] leading-[0.98] md:text-[72px]">This page is not in the document.</h1>
        <p className="rise d3 serif max-w-[44ch] text-[18px] md:text-[21px]">There is nothing at this address. A report link that has expired ends here too: reports are kept 7 days.</p>
        <div className="rise d4 flex flex-col gap-4 pt-1.5 md:flex-row md:items-center md:gap-6">
          <Link to="/scan" className="btn">Scan a document</Link>
          <Link to="/history" className="text-[14px]">History</Link>
        </div>
      </div>
    </section>
  )
}
