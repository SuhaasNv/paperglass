# Paperglass web app

React 19, TypeScript strict, Vite, Tailwind, TanStack Query, React Router. Talks to the backend over `/api/v1` on the same origin: Vite proxies it in development, nginx in the image (US-048).

Until the design pass (`docs/04-report-design/DESIGN_DIRECTION.md`) the pages are plumbing: semantic markup, no styles, every call wired. The design pass replaces the markup inside `src/pages/` and `src/app/Layout.tsx`; the API layer (`src/api/`) and the routes do not move.

```
npm install
npm run dev            # http://localhost:5173, backend expected on :8000 (PAPERGLASS_BACKEND_URL overrides)
npm run typecheck      # tsc -b, strict
npm run lint           # oxlint
npm test               # vitest, jsdom, fetch mocked
npm run test:e2e       # Playwright at 375, 768 and 1280 px; starts the backend on SQLite and Vite itself
npm run build          # dist/
```

Routes: `/` upload, `/scans/:id` results (the share link), `/history`, `/techniques`, `/about`. The e2e journey uploads `tests/fixtures/pdf/pdf.text.low_contrast/positive.pdf`, reads the verdict, opens the share link without a cookie, finds the report in history, runs a fingerprint, and checks that no page requests anything outside its own origin.
