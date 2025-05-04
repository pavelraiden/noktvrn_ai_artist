import { createBrowserRouter } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { Dashboard, ArtistsList, ArtistDetail } from './pages';

/**
 * Application router configuration
 */
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'artists',
        element: <ArtistsList />,
      },
      {
        path: 'artists/:id',
        element: <ArtistDetail />,
      },
    ],
  },
]);

export default router;