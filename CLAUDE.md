# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Teapot is a platform for creating and playing custom trading card games (TCGs) and board games. It uses a server-authoritative, event-sourced architecture.

## Service Architecture

Three services run in parallel:

| Service | Port | Directory | Description |
|---|---|---|---|
| **TeapotAPI** | 8000 | `TeapotAPI/` | Main FastAPI backend — auth, project management, game compilation |
| **CreatorAPI** | 8001 | `CreatorAPI/` | Multi-agent LLM pipeline — natural language → structured card JSON |
| **Frontend** | 5173 | `frontend/` | React/Vite workspace and creator tools |

`TeapotEngine/` is a shared Python rules engine imported by TeapotAPI (not a standalone service).

## Commands

### Service Management
```bash
./teapot.sh start all          # Start all services
./teapot.sh start teapot-api   # Start only TeapotAPI
./teapot.sh start creator-api  # Start only CreatorAPI
./teapot.sh start frontend     # Start only frontend
./teapot.sh stop all
./teapot.sh status all
# Logs written to logs/
```

### Frontend
```bash
cd frontend
npm run dev       # Dev server (port 5173)
npm run build     # Production build
npm run lint      # ESLint
npm run test      # Vitest (all tests)
npx vitest run path/to/test.ts  # Single test file
```

### Python Backend
```bash
python TeapotAPI/run.py                    # Run TeapotAPI directly
cd TeapotAPI && alembic upgrade head       # Apply DB migrations
cd TeapotAPI && alembic revision --autogenerate -m "description"  # New migration
```

### Environment
- `TeapotAPI/.env`: `DATABASE_URL`, `REDIS_URL`, `OPENAI_API_KEY`, `SECRET_KEY`
- `frontend/.env`: `VITE_API_URL=http://localhost:8000`, `VITE_CREATOR_API_URL=http://localhost:8001`
- Default DB: `postgresql+asyncpg://bryanjiang@localhost:5432/tcg_db`
- Default Redis: `redis://localhost:6379/0`

## Architecture

### Backend (TeapotAPI)
- **FastAPI** with async SQLAlchemy (PostgreSQL) and Redis
- **Repository pattern**: `app/repositories/` abstracts DB access
- **Service layer**: `app/services/` contains business logic
- **Routes**: `app/api/routes/` — `/api/auth/*` and `/api/projects/*`
- **Alembic** migrations in `TeapotAPI/alembic/versions/`

### Game Engine (TeapotEngine)
- Event-sourced: match state is an append-only event log with periodic snapshots
- **Actor-per-match** concurrency model — each match has an isolated `MatchActor`
- Deterministic RNG (SplitMix64/PCG) seeded per match for reproducibility
- Python sandbox for safe ability script execution
- Stack-based resolution for TCG priority/response mechanics

### CreatorAPI (Multi-Agent LLM)
- Specialized agents: Trigger, Effect, Condition, Requirement
- Uses OpenAI's API with tool-use and agent handoffs
- See `CreatorAPI/agent_architecture.txt` for pipeline design

### Frontend (React)
- **Redux Toolkit** + RTK Query for state and API calls (`src/app/store.ts`)
- **React Flow** (`@xyflow/react`) for the visual Blueprint-style scripting canvas in `src/features/workspace/`
- **React Router v6** for navigation
- **shadcn/ui** + Tailwind CSS for UI components (`src/components/ui/`)
- `src/features/` contains feature slices: `auth/`, `projects/`, `workspace/`, `ai-assistant/`

### Data Flow (Match Execution)
1. Client sends `Action` → TeapotAPI validates
2. `MatchActor` processes via reducer → runs Python trigger sandbox
3. Events emitted → broadcast via Redis pub/sub to connected clients
4. Events persisted to PostgreSQL (replayable)

### Workspace Canvas
The workspace feature (`src/features/workspace/`) is the main game-creation UI:
- `workspaceSlice.ts` — Redux slice managing the node/edge graph state
- `canvas/WorkspaceCanvas.tsx` — React Flow canvas component
- `nodes/CustomNode.tsx` — Custom node renderer
- Node types: Event (green), Function (blue), Flow Control (purple), Variable (yellow)

## Key Documentation
- `SystemArchitecture.md` — Comprehensive architecture reference (DB schema, scaling targets, testing strategy)
- `ImplementationPlan.md` — Phased delivery roadmap
- `CreatorAPI/agent_architecture.txt` — Multi-agent LLM system
- `example.py` — Demonstrates TeapotEngine usage
