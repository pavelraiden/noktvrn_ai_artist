import React from 'react';
import { createBrowserRouter } from 'react-router-dom';
import SpotifyLayout from './components/layout/SpotifyLayout';
import SpotifyDashboard from './pages/SpotifyDashboard';
import SpotifyArtistsList from './pages/SpotifyArtistsList';
import SpotifyArtistDetail from './pages/SpotifyArtistDetail';

/**
 * Application router with Spotify-styled routes
 */
const router = createBrowserRouter([
  {
    path: '/',
    element: <SpotifyLayout />,
    children: [
      {
        index: true,
        element: <SpotifyDashboard />,
      },
      {
        path: 'artists',
        element: <SpotifyArtistsList />,
      },
      {
        path: 'artists/:id',
        element: <SpotifyArtistDetail />,
      },
    ],
  },
]);

export default router;