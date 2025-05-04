import { createBrowserRouter } from 'react-router-dom';
import Layout from './components/layout/Layout'; // Adjusted path
import Dashboard from './pages/Dashboard'; // Adjusted path
import ArtistsList from './pages/ArtistsList'; // Adjusted path
import ArtistDetail from './pages/ArtistDetail'; // Adjusted path

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
      // TODO: Add routes for other pages like Settings, Profile, etc. if needed
    ],
    // TODO: Add ErrorBoundary component if implemented
    // errorElement: <ErrorPage />,
  },
  // TODO: Add routes for standalone pages like Login, Signup if needed
]);

export default router;

