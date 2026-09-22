import type { RouteObject } from 'react-router'

import { Layout } from './Layout'
import { AboutPage } from '../pages/AboutPage'
import { HistoryPage } from '../pages/HistoryPage'
import { LandingPage } from '../pages/LandingPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { ResultsPage } from '../pages/ResultsPage'
import { TechniquesPage } from '../pages/TechniquesPage'
import { UploadPage } from '../pages/UploadPage'

/** One route per screen. /scans/:id is the share-link contract and never moves. */
export const routes: RouteObject[] = [
  {
    element: <Layout />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: 'scan', element: <UploadPage /> },
      { path: 'scans/:id', element: <ResultsPage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'techniques', element: <TechniquesPage /> },
      { path: 'about', element: <AboutPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
