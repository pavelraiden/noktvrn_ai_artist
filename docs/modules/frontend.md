# Frontend Module Documentation

This document provides an overview of the frontend structure and setup for the AI Artist System.

## Structure

(To be updated with the full structure once all modules are integrated)

- `/frontend`: Root directory for the React application.
  - `package.json`: Project dependencies and scripts.
  - `vite.config.ts`: Vite build configuration.
  - `tailwind.config.js`: Tailwind CSS configuration.
  - `postcss.config.js`: PostCSS configuration.
  - `tsconfig.json`: TypeScript configuration.
  - `src/`: Source code directory.
    - `index.css`: Global styles.
    - `main.tsx`: Application entry point.
    - `App.tsx`: Root application component.
    - `routes.ts`: Application routing configuration.
    - `api/`: API service integration.
    - `assets/`: Static assets (images, fonts, etc.).
    - `components/`: Reusable UI components.
    - `contexts/`: React context providers.
    - `hooks/`: Custom React hooks.
    - `pages/`: Page-level components.
    - `types/`: TypeScript type definitions.
    - `utils/`: Utility functions.
  - `public/`: Static assets served directly.
  - `dist/`: Build output directory.

## Setup

1.  Navigate to the `frontend/` directory.
2.  Install dependencies: `npm install` (or `npm ci` if `package-lock.json` exists).
3.  Run development server: `npm run dev`.
4.  Build for production: `npm run build`.

## Key Libraries

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Zustand (for state management)
- React Router DOM (for routing)
- Recharts (for charts)
- clsx, tailwind-merge (for utility class merging)

## TODOs

- Complete integration of all UI modules.
- Finalize documentation for all submodules.
- Implement API connections to the backend.
- Add comprehensive testing.

