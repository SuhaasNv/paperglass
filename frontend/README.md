# Paperglass web app

React 19, TypeScript strict, Vite, Tailwind, TanStack Query, React Router. Talks to the backend over `/api/v1` on the same origin: Vite proxies it in development, nginx in the image (US-048).

Built to the chosen design, direction 1 "the Lens" (`docs/04-report-design/DESIGN_DIRECTION.md`): Instrument Serif, Hanken Grotesk and Geist Mono self-hosted through fontsource, paper and grain, one signal colour, and the lens that shows what the model reads only while the pointer is over a document. The API layer is `src/api/`; the screens are `src/pages/`; shared pieces are `src/components/`.

```
npm install
npm run dev            # http://localhost:5173, backend expected on :8000 (PAPERGLASS_BACKEND_URL overrides)
npm run typecheck      # tsc -b, strict
npm run lint           # oxlint
npm test               # vitest, jsdom, fetch mocked
npm run test:e2e       # Playwright at 375, 768 and 1280 px; starts the backend on SQLite and Vite itself
npm run build          # dist/
```

Routes: `/` landing, `/scan` upload, `/scans/:id` results (the share link), `/history`, `/techniques`, `/about`. The e2e journey checks that the lens opens only over the document and that no page scrolls sideways at 375, 768 or 1280 px, then uploads `tests/fixtures/pdf/pdf.text.low_contrast/positive.pdf`, reads the verdict, opens the share link without a cookie, finds the report in history, runs a fingerprint, and checks that no page requests anything outside its own origin.
