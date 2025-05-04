import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '../../utils/cn';

interface NavItemProps {
  to: string;
  label: string;
  icon: React.ReactNode;
  end?: boolean;
}

/**
 * Individual navigation item component
 */
const NavItem: React.FC<NavItemProps> = ({ to, label, icon, end = false }) => (
  <NavLink
    to={to}
    end={end}
    className={({ isActive }) =>
      cn(
        'flex items-center gap-3 px-4 py-2 rounded-md transition-colors text-base font-medium group',
        isActive 
          ? 'text-white bg-background-tinted' 
          : 'text-text-subdued hover:text-white'
      )
    }
  >
    <span className="text-lg">{icon}</span>
    <span>{label}</span>
  </NavLink>
);

/**
 * Section component for grouping navigation items
 */
const Section: React.FC<{ title?: string; children: React.ReactNode }> = ({ 
  title, 
  children 
}) => (
  <div className="mb-6">
    {title && (
      <h2 className="px-4 mb-2 text-xs uppercase tracking-widest font-bold text-text-subdued">
        {title}
      </h2>
    )}
    <nav className="space-y-1">
      {children}
    </nav>
  </div>
);

/**
 * Spotify-styled sidebar component
 */
const SpotifySidebar: React.FC = () => {
  return (
    <aside className="w-64 h-full bg-background-base flex flex-col">
      {/* Logo */}
      <div className="p-6">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <span role="img" aria-label="music" className="text-spotify-green">
            🎵
          </span>
          AI Artist Platform
        </h1>
      </div>
      
      {/* Main Navigation */}
      <div className="flex-1 overflow-y-auto px-2">
        <Section>
          <NavItem 
            to="/" 
            label="Home" 
            icon="🏠" 
            end 
          />
          <NavItem 
            to="/artists" 
            label="Artists" 
            icon="🎨" 
          />
          <NavItem 
            to="/trends" 
            label="Trends" 
            icon="📈" 
          />
          <NavItem 
            to="/logs" 
            label="Logs" 
            icon="📝" 
          />
          <NavItem 
            to="/settings" 
            label="Settings" 
            icon="⚙️" 
          />
        </Section>
        
        {/* Your Library Section */}
        <Section title="Your Library">
          <NavItem 
            to="/favourites" 
            label="Favorite Artists" 
            icon="⭐" 
          />
          <NavItem 
            to="/recent" 
            label="Recent Generations" 
            icon="🕒" 
          />
        </Section>
      </div>
      
      {/* Create Button */}
      <div className="p-4">
        <button className="w-full flex items-center justify-center gap-2 bg-spotify-green hover:bg-spotify-brightgreen text-black font-bold py-3 px-4 rounded-pill transition-colors">
          <span>+ Create New Artist</span>
        </button>
      </div>
      
      {/* Footer */}
      <div className="px-4 py-3 text-xs text-text-muted border-t border-background-highlight">
        <p>© 2025 AI Artist Platform</p>
      </div>
    </aside>
  );
};

export default SpotifySidebar;