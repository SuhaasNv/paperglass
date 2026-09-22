/** About: the three views, what the product does not do, the licence, the disclosure link. */
export function AboutPage() {
  return (
    <section aria-labelledby="about-heading">
      <h1 id="about-heading">About Paperglass</h1>
      <p>
        Paperglass shows the text a document gives to a model, compares it with the page it shows
        to a person and with the document's structure, and reports every place the three differ.
      </p>
      <h2>Three views</h2>
      <dl>
        <dt>View A</dt>
        <dd>What extractors return: the text a model reads.</dd>
        <dt>View B</dt>
        <dd>What a person sees: the rendered page, checked for ink, then read by OCR on crops.</dd>
        <dt>View C</dt>
        <dd>
          Structure: render modes, colours, sizes, clipping, layers, ActualText, ToUnicode maps,
          fonts, Word run properties and hidden parts.
        </dd>
      </dl>
      <h2>What it does not do</h2>
      <p>
        It does not judge visible text, detect malware or run anything inside a document. Hidden
        is not always malicious: alt text, ligature ActualText, OCR layers on scans and tagged
        structure are reported as benign-hidden. There is no score to rank people by.
      </p>
      <h2>Privacy</h2>
      <p>
        Files are scanned in memory and never stored. Reports are kept 7 days under an unguessable
        link and belong to the browser that made them. No accounts, no telemetry.
      </p>
      <h2>Licence and disclosure</h2>
      <p>
        Apache-2.0. Source, threat matrix and security policy:{' '}
        <a href="https://github.com/SuhaasNv/paperglass">github.com/SuhaasNv/paperglass</a>.
      </p>
    </section>
  )
}
