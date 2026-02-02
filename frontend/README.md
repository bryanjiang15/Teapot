# Teapot Frontend - TCG Creator

A beautiful, pastel/wood-themed React frontend for the Teapot game creation platform. Built with Vite, TypeScript, Tailwind CSS, and React Flow for Blueprint-style visual scripting.

## Features

- 🎨 **Pastel/Wood Theme**: Warm, inviting design with orange highlights
- 🔐 **Authentication**: Login/Register with JWT token management
- 📊 **Project Dashboard**: Manage multiple game projects with status tracking
- 🎮 **Workspace Canvas**: Blueprint-style visual scripting with React Flow
- 🤖 **AI Assistant**: Integrated chat panel for AI-powered game design help
- 🔗 **API Integration**: Connected to TeapotAPI and CreatorAPI backends

## Tech Stack

- **Framework**: Vite + React 18 + TypeScript
- **Styling**: Tailwind CSS with custom theme
- **UI Components**: shadcn/ui (customized)
- **State Management**: Redux Toolkit with RTK Query
- **Visual Scripting**: React Flow (@xyflow/react)
- **Routing**: React Router v6
- **Animations**: Framer Motion

## Getting Started

### Prerequisites

- Node.js 20.x or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_CREATOR_API_URL=http://localhost:8001
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Redux store configuration
│   ├── features/               # Feature-based modules
│   │   ├── auth/              # Authentication
│   │   ├── projects/          # Project management
│   │   ├── workspace/         # Canvas & visual scripting
│   │   └── ai-assistant/      # AI chat panel
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   └── shared/            # Reusable custom components
│   ├── layouts/               # Page layouts
│   ├── lib/                   # Utilities & API clients
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript type definitions
│   └── styles/                # Global styles
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Design System

### Color Palette

- **Primary Orange**: `#FF8C42` - CTAs, highlights, active states
- **Cream Background**: `#FFF8F0` - Main background
- **Beige Light**: `#F5EBE0` - Secondary background
- **Wood Brown**: `#8B7355` - Borders, accents
- **Pastel Colors**:
  - Green: `#B8DDB8` - Event nodes
  - Blue: `#B8D8E8` - Function nodes
  - Purple: `#D8C7E8` - Flow control nodes
  - Yellow: `#F5E6B8` - Variable nodes

### Typography

- **Headings**: Poppins (Semi-Bold, 600)
- **Body**: Inter (Regular, 400; Medium, 500)
- **Code**: JetBrains Mono

## Blueprint Node System

The visual scripting system uses React Flow with custom nodes:

- **Event Nodes** (Green): Entry points for game logic
- **Function Nodes** (Blue): Actions that modify game state
- **Flow Control Nodes** (Purple): Conditional execution
- **Variable Nodes** (Yellow): Data access and manipulation
- **Target Selector Nodes** (Orange): Query and filter game objects

Nodes feature:
- Type-safe connections
- Execution flow (white) vs data flow (colored)
- Inline parameter editing
- Multiple input/output ports

## Backend Integration

### TeapotAPI
- Authentication endpoints
- Project CRUD operations
- Game rules management

### CreatorAPI
- AI ability parsing
- Card generation
- Rule suggestions

## Development Notes

- The workspace uses mock data for now. Connect to real backend endpoints by implementing the API layer.
- AI chat responses are simulated. Integrate with actual LLM endpoints.
- Node system is designed to scale from simple blocks to complex Blueprint-like graphs.

## Contributing

1. Follow the existing code structure
2. Use TypeScript for type safety
3. Follow the design system for consistent UI
4. Test with both light themes

## License

This project is part of the Teapot platform.
