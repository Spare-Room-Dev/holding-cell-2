# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 01-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 01-foundation
**Areas discussed:** Project structure, Type sharing, Socket config, Logging, State management, Dev scripts, Backend organization

---

## Project Structure

| Option | Description | Selected |
|--------|-------------|----------|
| backend/ + frontend/ directories | Clean separation, npm workspaces, root scripts to run both. Simple and standard for this size. | ✓ |
| Single Next.js app + Python server/ | All frontend in root, backend in server/. Keeps Next.js conventions. | |
| Monorepo tool (Turborepo/Nx) | Less common for this stack, more tooling overhead. | |

**User's choice:** backend/ + frontend/ directories (recommended)
**Notes:** User selected all recommended options throughout discussion.

---

## Type Sharing

| Option | Description | Selected |
|--------|-------------|----------|
| Separate definitions in each codebase | Python Pydantic model in backend, TypeScript interface in frontend. Keep in sync manually. Simple, no build step. | ✓ |
| Auto-generate TypeScript from Python models | Generate TypeScript from Pydantic. Single source of truth, but adds complexity for Phase 1. | |
| Shared JSON Schema + codegen | Schema file both codebases import. Extra dependency, overkill for one type. | |

**User's choice:** Separate definitions in each codebase (recommended)
**Notes:** Simple for one AttackEvent type, revisit if types grow.

---

## Socket CORS

| Option | Description | Selected |
|--------|-------------|----------|
| Allow localhost:3000 only | Development only. Production CORS handled separately in Weekend 2. | ✓ |
| Allow all origins (*:*) | Maximum flexibility, slight security trade-off. | |
| Allow localhost:3000 and localhost:8000 | Most restrictive, requires exact port. | |

**User's choice:** Allow localhost:3000 only (recommended)
**Notes:** Production CORS deferred to Weekend 2 deployment.

---

## Backend Logging

| Option | Description | Selected |
|--------|-------------|----------|
| Colored archetype tag + attack summary | Timestamp, archetype, IP. Easy to read, matches PLAN.md example. | ✓ |
| Plain text: attack event received | Minimal output, just shows activity. | |
| Full JSON dump of each event | For debugging. Overkill for fake data. | |

**User's choice:** Colored archetype tag + attack summary (recommended)
**Notes:** Example: `[BOTNET_DRONE] 203.0.113.42`

---

## Frontend State Management

| Option | Description | Selected |
|--------|-------------|----------|
| React Context + useReducer | Lightweight, built into React, no extra dependencies. Perfect for Phase 1's simple needs. | ✓ |
| Zustand store | Popular, simple hooks API. Adds a dependency. | |
| Local useState in page.tsx | Simplest for small state. Gets complex as app grows. | |

**User's choice:** React Context + useReducer (recommended)
**Notes:** Context provides connection status, attacks array, connect/disconnect handlers.

---

## Dev Scripts

| Option | Description | Selected |
|--------|-------------|----------|
| Root package.json with concurrently | Node-centric, works with npm workspaces. Simple and standard. | ✓ |
| Makefile with dev targets | More flexible for Python + Node mix. Requires make on system. | |
| Separate scripts (no unified dev:all) | Two terminal windows. No tooling needed. | |

**User's choice:** Root package.json with concurrently (recommended)
**Notes:** Scripts: dev:backend, dev:frontend, dev:all.

---

## Backend Organization

| Option | Description | Selected |
|--------|-------------|----------|
| Single backend/ directory | All Python code in backend/. Simple for this project size. | ✓ |
| backend/app/ with routers/ subdirs | Better for larger projects. Overkill here. | |

**User's choice:** Single backend/ directory (recommended)
**Notes:** Flat structure: main.py, attack_generator.py, models.py, archetypes.py.

---

## Claude's Discretion

- Exact ping/pong intervals for Socket.io (use defaults)
- Exact Tailwind configuration (follow DESIGN.md tokens)
- Framer Motion version pinning (use latest 11.x)
- Color utility implementation for archetype tags

## Deferred Ideas

None — discussion stayed within phase scope.