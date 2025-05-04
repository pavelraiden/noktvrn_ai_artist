# AI Artist Platform Frontend Flow

This document provides a high-level overview of the frontend architecture, data flow, and design patterns.

## 📂 Folder Structure

The frontend is organized in a modular, feature-based structure:

```
src/
├── assets/            # Static resources like images, icons
├── components/        # Reusable UI components
│   ├── charts/        # Data visualization components
│   ├── layout/        # Layout components (Header, Sidebar)
│   ├── artist/        # Artist-related components
│   ├── chat/          # Chat-related components
│   └── ui/            # Base UI components (Button, Card, etc.)
├── hooks/             # Custom React hooks
├── pages/             # Page components that correspond to routes
├── services/          # API services and data fetching
├── store/             # Global state management
├── test/              # Test files
├── types/             # TypeScript type definitions
└── utils/             # Utility functions
```

## 🔄 Data Flow

The application follows a unidirectional data flow pattern:

1. **User interaction** triggers an action
2. **API calls** are made using React Query
3. **Server data** is cached in React Query
4. **UI updates** are rendered based on query state
5. **Global state** managed by Zustand for cross-component state

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│    User     │─────▶│   React     │─────▶│    API      │
│ Interaction │      │ Components  │      │  Services   │
└─────────────┘      └─────────────┘      └─────────────┘
                           ▲                     │
                           │                     │
                           │                     ▼
                    ┌──────┴──────┐      ┌─────────────┐
                    │   Zustand   │◀─────│React Query  │
                    │    Store    │      │    Cache    │
                    └─────────────┘      └─────────────┘
```

## 🧩 Component Design

The component architecture follows these principles:

1. **Composition over inheritance**
   - Smaller, specialized components composed together
   - Higher-order components used sparingly

2. **Container/Presentation pattern**
   - Pages/containers handle data fetching and state
   - Presentation components are pure and focus on UI

3. **Component responsibilities**
   - Each component has a single responsibility
   - Props are typed with TypeScript interfaces
   - JSDoc comments document component purpose and usage

## 🔄 State Management

The application uses a hybrid state management approach:

1. **React Query** for server state
   - API data fetching and caching
   - Automatic refetching and invalidation
   - Loading, error, and success states

2. **Zustand** for client state
   - Cross-component shared state
   - Minimal and selective global state
   - Artist selection and recently viewed tracking

3. **React state** for local component state
   - Form inputs and UI state
   - Component-specific state that doesn't need to be shared

## 🧪 Testing Strategy

The testing approach follows these principles:

1. **Component tests**
   - Test component rendering and behavior
   - Mock API calls and state

2. **Hook tests**
   - Test custom hooks in isolation
   - Verify state management logic

3. **Integration tests**
   - Test component interactions
   - Verify data flow between components

## 🛠️ Adding New Features

To add new features:

1. **Define types** in the appropriate files under `types/`
2. **Create API services** in `services/api.ts`
3. **Build UI components** in the appropriate folder under `components/`
4. **Add page components** in `pages/` if needed
5. **Update routes** in `routes.tsx` if adding new pages
6. **Add tests** for new components and features

## 🎨 Styling Conventions

The application uses Tailwind CSS with these conventions:

1. **Component-based styling**
   - Styles are applied directly to components with Tailwind classes
   - Common patterns are extracted into reusable components

2. **Responsive design**
   - Mobile-first approach
   - Breakpoints used consistently (`sm`, `md`, `lg`, `xl`)

3. **Theme consistency**
   - Colors follow the design system defined in `tailwind.config.js`
   - Spacing and sizing use Tailwind's built-in scale

## 🌐 API Integration

Backend API integration follows these patterns:

1. **Centralized API services**
   - All API calls are defined in `services/api.ts`
   - Typed request and response interfaces

2. **React Query for data fetching**
   - Queries for retrieving data
   - Mutations for updating data
   - Automatic caching and revalidation

3. **WebSockets for real-time communication**
   - Custom hook for WebSocket connection
   - Event-based communication pattern
