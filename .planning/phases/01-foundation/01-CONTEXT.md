# Phase 1: Foundation - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Backend server runs and emits fake attack events via Socket.io; frontend connects and displays connection status. The core real-time pipeline with simulated attack data. This phase establishes the foundation for the full dashboard — no jail cell visualization, prisoner avatars, or stats panel yet (those are Phase 2+).

</domain>

<decisions>
## Implementation Decisions

### Project Structure
- **D-01:** Two directories at root: `backend/` for Python, `frontend/` for Next.js
- **D-02:** Root `package.json` with npm workspaces for unified dev scripts
- **D-03:** No shared types directory — each codebase maintains its own type definitions

### Socket Configuration
- **D-04:** CORS allows `localhost:3000` only (development)
- **D-05:** Reconnection: exponential backoff (1s, 2s, 4s, max 30s) per RTCL-02
- **D-06:** Events during disconnect are lost — acceptable for Approach A v1 (RTCL-05)

### Backend Architecture
- **D-07:** Single `backend/` directory — all Python code flat (not `backend/app/` with routers)
- **D-08:** Attack generator emits every 3-8 seconds (randomized interval)
- **D-09:** Console logging: colored archetype tag + attack summary (timestamp, archetype, IP)

### Type Strategy
- **D-10:** `AttackEvent` type defined separately in each codebase
- **D-11:** Python: Pydantic model in `backend/models.py`
- **D-12:** TypeScript: interface in `frontend/src/types/attack.ts`
- **D-13:** Keep in sync manually — simple for one type, revisit if types grow

### Frontend State
- **D-14:** React Context + useReducer for connection state and received attacks
- **D-15:** Context provides: connection status, attacks array, connect/disconnect handlers
- **D-16:** Dark mode primary by default; light mode toggle functional (FE-05)

### Dev Scripts
- **D-17:** Root `package.json` with `concurrently` for `dev:all`
- **D-18:** Scripts: `dev:backend` (uvicorn), `dev:frontend` (next dev), `dev:all` (both)
- **D-19:** Python dependencies in `backend/requirements.txt`
- **D-20:** Node dependencies in `frontend/package.json` + root `package.json` (workspace root)

### Claude's Discretion
- Exact ping/pong intervals for Socket.io (use defaults)
- Exact Tailwind configuration (follow DESIGN.md tokens)
- Framer Motion version pinning (use latest 11.x)
- Color utility implementation for archetype tags

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Decisions
- `PLAN.md` — Architecture diagram, data model, API contracts, component specs, file structure, error handling
- `DESIGN.md` — Color tokens (Phosphor Green `#00FF88`), typography (Satoshi, DM Sans, IBM Plex Mono), spacing scale, motion timing

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 1 requirements: BACK-01 to BACK-09, RTCL-01 to RTCL-05, FE-01 to FE-06, DEV-01 to DEV-05
- `.planning/PROJECT.md` — Tech stack (FastAPI, python-socketio async, Next.js 14 App Router), key decisions table

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
None — this is a greenfield project.

### Established Patterns
None — patterns will be established in this phase.

### Integration Points
- `backend/main.py` → FastAPI + Socket.io server on port 8000
- `frontend/src/lib/socket.ts` → Socket.io client connecting to ws://localhost:8000
- `frontend/src/app/page.tsx` → Dashboard receiving attack events

</code_context>

<specifics>
## Specific Ideas

- PLAN.md architecture diagram shows clean separation: AttackGenerator emits to SocketServer, which broadcasts to browser
- Colored archetype tags in logs: `[BOTNET_DRONE] 203.0.113.42` style output
- Connection status: "LIVE" badge with phosphor green glow pulse, "SIGNAL LOST" banner during disconnect
- Empty state for jail cell: "The cell is empty. Waiting for attackers..." (Phase 2)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-24*