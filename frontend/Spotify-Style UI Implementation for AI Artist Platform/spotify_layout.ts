import React from 'react';
import { Outlet } from 'react-router-dom';
import SpotifyHeader from './SpotifyHeader';
import SpotifySidebar from './SpotifySidebar';
import SpotifyPlayer from './SpotifyPlayer';
import ErrorBoundary from '../ui/ErrorBoundary';

/**
 * Main layout component inspired by Spotify's design
 * Includes sidebar, header, content area, and audio player
 */
const SpotifyLayout: React.FC = () => {
  return (
    <div className="flex flex-col h-screen bg-background-base text-text-base">
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <SpotifySidebar />

        {/* Main content area */}
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Header */}
          <SpotifyHeader />
          
          {/* Content */}
          <main className="flex-1 overflow-y-auto p-8">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </main>
        </div>
      </div>

      {/* Footer player */}
      <SpotifyPlayer />
    </div>
  );
};

export default SpotifyLayout;