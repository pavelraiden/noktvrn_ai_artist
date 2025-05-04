# AI Artist System - Frontend

This directory contains the React frontend application for the AI Artist System dashboard.

## Integration Process

The current frontend structure was integrated from the `AI Artist interface-20250503T235038Z-001.zip` archive provided.

1.  The `frontend/` directory was cleared and recreated.
2.  The archive was extracted into `frontend/`.
3.  Extraction completeness was verified by comparing the output of `find frontend -type f | sort` against `unzip -l <archive>.zip | awk 
    '{print $4}' | grep -v 
    '/$' | sort` using `diff`. This check confirmed all files were extracted correctly.
4.  Dependencies were installed using `npm install`.
5.  UI components, types, utilities, hooks, and routing were implemented based on the extracted templates.
6.  Tailwind CSS was configured and verified.
7.  The project was successfully built using `npm run build`.

## Project Structure

Below is the structure of the relevant source files and configuration files within the `frontend/` directory (excluding `node_modules`, `dist`, and temporary archive extraction folders):

```
/home/ubuntu/ai_artist_system_clone/frontend
├── package.json
├── package-lock.json
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── src
    ├── App.tsx
    ├── index.css
    ├── main.tsx
    ├── routes.ts
    ├── api
    │   └── api_services.ts
    ├── assets
    ├── components
    │   ├── artists
    │   │   ├── ArtistCard.tsx
    │   │   └── ArtistFilter.tsx
    │   ├── chat
    │   │   ├── ChatMessage.tsx
    │   │   └── ChatWindow.tsx
    │   ├── charts
    │   │   ├── BarLineChart.tsx
    │   │   └── PieChart.tsx
    │   ├── layout
    │   │   ├── Header.tsx
    │   │   ├── Layout.tsx
    │   │   └── Sidebar.tsx
    │   └── ui
    │       ├── Button.tsx
    │       ├── Card.tsx
    │       ├── ErrorBoundary.tsx
    │       └── Tab.tsx
    ├── contexts
    │   └── artist_store.ts
    ├── hooks
    │   └── socket_hook.ts
    ├── pages
    │   ├── ArtistDetail.tsx
    │   ├── ArtistsList.tsx
    │   └── Dashboard.tsx
    ├── styles
    ├── types
    │   ├── artist_types.ts
    │   ├── chat_types.ts
    │   ├── index_types.ts
    │   └── stats_types.ts
    └── utils
        ├── cn.ts
        ├── cn_utils.ts
        ├── formatters.ts
        └── test_formatters.ts
```

*(Note: The structure above is simplified from the `find` output for readability. It includes key source files and configuration.)*

## Key Libraries

*   React
*   Vite
*   TypeScript
*   Tailwind CSS
*   React Router DOM
*   @tanstack/react-query
*   Zustand
*   axios
*   socket.io-client
*   recharts

## Available Scripts

In the project directory, you can run:

*   `npm run dev`: Runs the app in development mode.
*   `npm run build`: Builds the app for production.
*   `npm run lint`: Lints the codebase.
*   `npm run preview`: Serves the production build locally.
*   `npm run test`: Runs tests using Vitest.

