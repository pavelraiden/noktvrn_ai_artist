import { Outlet } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header or Sidebar could go here */}
      <header className="p-4 bg-gray-100 border-b">
        <h1>AI Artist Dashboard</h1>
        {/* Basic Navigation Links (can be improved later) */}
        <nav className="mt-2">
          <a href="/" className="mr-4">Dashboard</a>
          <a href="/artists">Artists</a>
        </nav>
      </header>

      {/* Main content area where nested routes will render */}
      <main className="flex-grow p-4">
        <Outlet />
      </main>

      {/* Footer could go here */}
      <footer className="p-4 bg-gray-100 border-t text-center text-sm">
        AI Artist System © 2025
      </footer>
    </div>
  );
}

export default App;

