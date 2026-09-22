/** About: the three views, what the product does not do, privacy, licence and disclosure. */
export function AboutPage() {
  return (
    <section aria-labelledby="about-heading" className="grid grid-cols-1 gap-8 px-5 pt-10 pb-16 md:grid-cols-12 md:gap-x-6 md:px-14 md:pt-14">
      <nav aria-label="Contents" className="rise d1 hidden flex-col gap-2.5 text-[14px] md:col-span-3 md:flex">
        <span className="eyebrow">Contents</span>
        <a href="#what" className="text-ink no-underline">What it is</a><a href="#views" className="text-ink no-underline">The three views</a><a href="#not" className="text-ink no-underline">What it does not do</a><a href="#privacy" className="text-ink no-underline">Privacy</a><a href="#licence" className="text-ink no-underline">Licence and disclosure</a>
      </nav>
      <article className="flex flex-col gap-7 md:col-span-8 md:col-start-4">
        <div className="rise d1 flex flex-col gap-3">
          <span className="eyebrow">About</span>
          <h1 id="about-heading" className="text-[52px] leading-[0.95] md:text-[88px]">A magnifying glass over paper.</h1>
        </div>
        <p className="rise d2 serif max-w-[44ch] text-[19px] leading-[1.35] md:text-[24px]">Paperglass shows the text a document gives to a model, compares it with the page it shows to a person and with the document's structure, and reports every place the three differ: technique, page, region, the hidden text, the rendered crop, the exact object that hid it, and a command that reproduces the finding without trusting Paperglass.</p>
        <h2 id="views" className="rise d3 border-t border-ink pt-6 text-[36px] md:text-[44px]">The three views</h2>
        <dl className="rise d3 m-0 grid grid-cols-[56px_1fr] gap-x-6 gap-y-4 text-[16px] leading-[1.5] md:grid-cols-[120px_1fr] md:text-[17px]">
          <dt className="ital text-[26px]">A</dt><dd className="m-0">What the model receives: the text an extractor returns, with the position and font of every run. The report names the extractor.</dd>
          <dt className="ital text-[26px]">B</dt><dd className="m-0">What a person sees: the page rendered at 150 dpi, every extracted run checked for ink, then OCR on the suspect crops only.</dd>
          <dt className="ital text-[26px]">C</dt><dd className="m-0">What the document contains: render modes, colours, sizes, clipping, layers, ActualText, ToUnicode maps, fonts, Word run properties and hidden parts.</dd>
        </dl>
        <p className="rise d4 serif max-w-[40ch] text-[19px] md:text-[22px]">Paperglass finds disagreement between these views. A candidate from View C is <em className="ital">possible</em> until View B or a self-proving mechanism confirms it; the verdict comes from confirmed findings only. There is no score to rank people by.</p>
        <h2 id="not" className="rise d4 border-t border-ink pt-6 text-[36px] md:text-[44px]">What it does not do</h2>
        <p className="rise d5 max-w-[66ch] text-[16px] leading-[1.55] md:text-[17px]">It does not judge visible text, detect malware or run anything inside a document. Hidden is not always malicious: alt text, ligature ActualText, OCR layers on scans and tagged structure are reported as benign-hidden, never as an attack. Paperglass never decides an outcome for a person; the verdict is advice with evidence.</p>
        <div className="rise d5 grid grid-cols-1 gap-8 border-t border-ink pt-6 md:grid-cols-2 md:gap-x-8">
          <div className="flex flex-col gap-2.5"><h2 id="privacy" className="text-[32px]">Privacy</h2><p className="text-[16px] leading-[1.55]">Files are scanned in memory and never stored. Reports are kept 7 days under an unguessable link and belong to the browser that made them. No accounts, no telemetry, no external requests.</p></div>
          <div className="flex flex-col gap-2.5"><h2 id="licence" className="text-[32px]">Licence and disclosure</h2><p className="text-[16px] leading-[1.55]">Apache-2.0. Source, threat matrix and the security policy with its private disclosure channel: <a href="https://github.com/SuhaasNv/paperglass">github.com/SuhaasNv/paperglass</a>.</p></div>
        </div>
      </article>
    </section>
  )
}
