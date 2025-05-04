import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';

/**
 * Spotify-style header component with navigation controls, search bar,
 * and user controls
 */
const SpotifyHeader: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, setTheme } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  
  // Handle search submission
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };
  
  // Handle navigation
  const handleBack = () => {
    navigate(-1);
  };
  
  const handleForward = () => {
    navigate(1);
  };

  return (
    <header className="bg-background-elevated px-8 py-4 flex items-center justify-between sticky top-0 z-10 backdrop-blur-md bg-opacity-95">
      {/* Navigation Controls */}
      <div className="flex items-center gap-4">
        <div className="flex gap-2">
          <button 
            onClick={handleBack}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-background-press text-white"
            aria-label="Go back"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </button>
          
          <button 
            onClick={handleForward}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-background-press text-white"
            aria-label="Go forward"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </button>
        </div>
        
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="relative">
          <input
            type="search"
            placeholder="Search artists..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-background-highlight text-white placeholder-text-subdued px-3 py-2 pl-10 rounded-pill w-64 focus:outline-none focus:ring-2 focus:ring-spotify-green"
          />
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-subdued">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          </div>
        </form>
      </div>
      
      {/* User Controls */}
      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="text-text-subdued hover:text-white p-2 rounded-full"
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? (
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>
        
        {/* Notifications */}
        <button
          className="text-text-subdued hover:text-white p-2 rounded-full relative"
          aria-label="Notifications"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          {/* Notification indicator */}
          <div className="absolute top-1 right-1 w-2 h-2 bg-spotify-green rounded-full"></div>
        </button>
        
        {/* User Profile */}
        <button
          className="flex items-center gap-2 bg-background-press hover:bg-background-highlight rounded-pill p-0.5 pl-1 pr-3 transition-colors"
        >
          <div className="w-7 h-7 rounded-full bg-spotify-purple flex items-center justify-center text-white font-medium">
            A
          </div>
          <span className="text-sm font-medium text-white">Admin</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
      </div>
    </header>
  );
};

export default SpotifyHeader;