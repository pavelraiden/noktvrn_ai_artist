import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

/**
 * Navigation item properties
 */
interface NavItem {
  to: string;
  label: string;
  icon: string;
}

/**
 * Navigation items for the sidebar
 */
const navItems: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/artists', label: 'Artists', icon: '🎨' },
];

/**
 * Sidebar component for main navigation
 * @returns Sidebar component
 */
const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside 
      className={`${
        collapsed ? 'w-16' : 'w-64'
      } bg-white border-r border-gray-200 h-full flex flex-col transition-width duration-300 ease-in-out`}
    >
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        {!collapsed && (
          <h1 className="text-xl font-bold text-primary-700">AI Artist</h1>
        )}
        <button 
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-md hover:bg-gray-100"
        >
          {collapsed ? '→' : '←'}
        </button>
      </div>
      
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center p-2 rounded-lg ${
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
                end
              >
                <span className="mr-2">{item.icon}</span>
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      {!collapsed && (
        <div className="p-4 border-t border-gray-200">
          <p className="text-sm text-gray-500">© 2025 AI Artist Platform</p>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
