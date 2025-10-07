# Teapot Platform

## Overview
Teapot is an end-to-end platform for building and playing custom trading card games, combining creator tooling, a server-authoritative backend, and a deterministic match engine to deliver low-latency, replayable battles for players, creators, and moderators alike.【F:SystemArchitecture.md†L5-L60】

## Repository Structure
- **TeapotAPI/** – FastAPI backend handling authentication, data access, and foundational gameplay services with JWT auth, SQLAlchemy models, and health monitoring in place.【F:TeapotAPI/docs/README.md†L1-L66】
- **TeapotEngine/** – Shared Python engine that powers event-sourced matches, flexible JSON rulesets, and deterministic resolution via seeded RNG and an actor-based architecture.【F:TeapotEngine/README.md†L1-L152】
- **CreatorAPI/** – Multi-agent LLM pipeline that parses natural-language ability descriptions into structured JSON using specialized trigger, effect, target, and requirement agents working in parallel with recursive post-processing.【F:CreatorAPI/agent_architecture.txt†L1-L168】
- **ImplementationPlan.md** – Detailed multi-phase roadmap covering backend, engine, client, and AI tooling deliverables, tech stacks, and testing strategy.【F:ImplementationPlan.md†L1-L120】
- **SystemArchitecture.md** – High-level product vision, cross-system architecture, and non-functional targets spanning the React app, backend, and Unity WebGL client.【F:SystemArchitecture.md†L5-L200】

## Key Technical Achievements
- **Server-authoritative architecture** with event sourcing, deterministic reducers, and WebSocket fan-out that keeps Unity clients as thin renderers while ensuring authoritative resolution and replayability.【F:SystemArchitecture.md†L15-L160】
- **Reusable ruleset-driven engine** supporting custom actions, stack-based resolution, and JSON IR-defined mechanics that can be embedded by both client and server services.【F:TeapotEngine/README.md†L1-L129】
- **LLM-assisted creator tooling** featuring parallel agent orchestration, recursive amount resolution, and tool-validated outputs to transform prose abilities into game-ready data models.【F:CreatorAPI/agent_architecture.txt†L5-L168】
- **Production-ready backend foundations** including JWT-secured auth flows, repository-driven data access, and a documented project layout ready for expansion into matches, rulesets, and AI endpoints.【F:TeapotAPI/docs/README.md†L29-L73】

## Tech Stack Highlights
- **Backend**: FastAPI, PostgreSQL, Redis, Pydantic, SQLAlchemy, Alembic, JWT-based authentication, and asyncio-driven event processing.【F:ImplementationPlan.md†L16-L118】【F:SystemArchitecture.md†L74-L139】
- **Match Engine**: Python actor model with event sourcing, deterministic RNG, JSON ruleset IR, and LIFO event stacks for resolution.【F:TeapotEngine/README.md†L5-L129】
- **Creator Tools**: Async multi-agent LLM workflows with schema validation tools and recursive data enrichment for complex ability parsing.【F:CreatorAPI/agent_architecture.txt†L5-L168】
- **Client & Runtime**: Unity WebGL renderer applying authoritative state diffs, coroutine-driven animation queues, and optional prediction for responsive UX.【F:SystemArchitecture.md†L168-L200】

## Getting Started
1. **Backend API** – Install dependencies, configure environment variables, and run `python run.py` to start the FastAPI service (see `TeapotAPI/docs/README.md`).【F:TeapotAPI/docs/README.md†L3-L73】
2. **Match Engine Library** – Install with `pip install -e .` from `TeapotEngine/` and use the `GameEngine` and `RulesetIR` primitives to script matches.【F:TeapotEngine/README.md†L13-L150】
3. **Creator Pipeline** – Explore the `Generate_Ability` workflow and agent registry inside `CreatorAPI/` to integrate the multi-agent ability parser into your tooling stack.【F:CreatorAPI/agent_architecture.txt†L5-L168】

## Next Steps
- Expand REST coverage with matches, card, and ruleset endpoints, and add WebSocket plus Redis support for live play.【F:TeapotAPI/docs/README.md†L67-L73】
- Follow the implementation roadmap to bring event sourcing, Unity state management, and React-based creator experiences online across upcoming phases.【F:ImplementationPlan.md†L1-L120】【F:SystemArchitecture.md†L15-L200】
- Productize AI generation flows by connecting prompt-based card, art, and rules suggestions into moderation and publishing workflows outlined in the architecture plan.【F:SystemArchitecture.md†L45-L165】【F:CreatorAPI/agent_architecture.txt†L5-L168】
