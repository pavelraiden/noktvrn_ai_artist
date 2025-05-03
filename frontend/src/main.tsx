import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App.tsx';
import DashboardPage from './pages/DashboardPage.tsx';
import ArtistsListPage from './pages/ArtistsListPage.tsx';
import ArtistDetailPage from './pages/ArtistDetailPage.tsx';
import './index.css';

// Create a client
const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Wrap routes in the App component which can act as a layout */}
          <Route path="/" element={<App />}>
            <Route index element={<DashboardPage />} />
            <Route path="artists" element={<ArtistsListPage />} />
            <Route path="artists/:id" element={<ArtistDetailPage />} />
            {/* Add other routes here as needed */}
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);

