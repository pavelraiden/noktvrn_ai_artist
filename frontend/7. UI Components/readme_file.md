# AI Artist Platform Frontend

A production-grade React frontend for the AI Artist Platform, built with TypeScript, Tailwind CSS, React Query, and more.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test
```

## 📋 Features

- Modern React and TypeScript
- Full integration with FastAPI backend
- Responsive dashboard with interactive charts
- Real-time chat via WebSockets
- State management with React Query and Zustand
- Styling with Tailwind CSS
- Comprehensive UI component system
- Unit testing with Vitest and React Testing Library

## 📦 Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/            # Static resources
│   ├── components/        # UI components
│   │   ├── charts/        # Chart components
│   │   ├── layout/        # Layout components
│   │   ├── artist/        # Artist-related components
│   │   ├── chat/          # Chat components
│   │   └── ui/            # Base UI components
│   ├── hooks/             # Custom React hooks
│   ├── pages/             # Page components
│   ├── services/          # API services
│   ├── store/             # State management
│   ├── test/              # Tests
│   ├── types/             # TypeScript types
│   └── utils/             # Utility functions
├── .eslintrc.js           # ESLint configuration
├── index.html             # HTML template
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── vite.config.ts         # Vite configuration
```

## 🔄 API Integration

The frontend integrates with the following endpoints:

- `GET /api/stats` - Dashboard statistics
- `GET /api/artists` - List of artists
- `GET /api/artists/:id` - Artist details
- `GET /api/artists/:id/logs` - Artist logs
- `POST /api/artists/:id/generate` - Generate new content
- WebSocket at `ws://localhost:8000/ws/chat/:artistId` - Real-time chat

## 🧪 Testing

The project uses Vitest and React Testing Library for testing:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 🐳 Docker

The project includes Docker configuration for production deployment:

```bash
# Build Docker image
docker build -t ai-artist-frontend .

# Run container
docker run -p 80:80 ai-artist-frontend
```

## 🔄 CI/CD

GitHub Actions workflow is configured to automatically:

1. Install dependencies
2. Type check with TypeScript
3. Run linting
4. Run tests
5. Build the project

## 📚 Additional Information

- Node.js 18+ required
- Backend server should be running at http://localhost:8000
- Recommended VSCode extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense

After implementing this frontend, please verify the UI by running `npm run dev` and connecting to the backend, then commit all changes to `main` with messages prefixed `feat(ui):`.
