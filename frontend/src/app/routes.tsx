import type { RouteObject } from 'react-router'

import { Layout } from './Layout'
import { AboutPage } from '../pages/AboutPage'
import { HistoryPage } from '../pages/HistoryPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { ResultsPage } from '../pages/ResultsPage'
import { TechniquesPage } from '../pages/TechniquesPage'
import { UploadPage } from '../pages/UploadPage'

/** One route per screen. Paths are part of the share-link contract, so they do not move. */
export const routes: RouteObject[] = [
  {
    element: <Layout />,
    children: [
      { index: true, element: <UploadPage /> },
      { path: 'scans/:id', element: <ResultsPage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'techniques', element: <TechniquesPage /> },
      { path: 'about', element: <AboutPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
