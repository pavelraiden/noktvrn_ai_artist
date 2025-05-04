import React from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Header component for the application
 * @returns Header component
 */
const Header: React.FC = () => {
  const location = useLocation();
  
  /**
   * Gets the page title based on the current path
   * @returns Page title
   */
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path.startsWith('/artists') && path.length > '/artists'.length)
      return 'Artist Details';
    if (path === '/artists') return 'Artists';
    return 'AI Artist Platform';
  };

  return (
    <header className="bg-white border-b border-gray-200 py-4 px-6 flex items-center justify-between">
      <h1 className="text-xl font-semibold text-gray-800">{getPageTitle()}</h1>
      <div className="flex items-center space-x-4">
        <button className="p-2 text-gray-600 hover:text-gray-900">
          <span role="img" aria-label="notifications">🔔</span>
        </button>
        <div className="relative">
          <button className="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700">
              <span className="text-sm font-medium">AD</span>
            </div>
            <span>Admin</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
