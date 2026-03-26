# Phase 7: Persistence & Analytics — Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

All visitors see the same attack history with lifetime stats and top attack analytics. Attacks persist across server restarts, new visitors immediately see existing history, and analytics aggregate attack data in real-time. This phase adds persistence and analytics to the real-time pipeline established in Phase 6. No new attack sources, no public deployment yet (Phase 8).

</domain>

<decisions>
## Implementation Decisions

### Persistence Storage
- **D-01:** JSON file for attack history — simple, Docker volume-friendly, easy to inspect
- **D-02:** `attacks.json` stored in shared Docker volume (same pattern as Cowrie logs)
- **D-03:** Persist every attack immediately after emission — no data loss on crash
- **D-04:** Last 20 attacks stored as array, newest first, capped at 20 items

### State Sharing & Connection
- **D-05:** New visitors receive history on socket connect via `attack_history` event
- **D-06:** Server maintains in-memory copy of last 20 attacks for fast history delivery
- **D-07:** On server startup, load history from JSON file into memory
- **D-08:** After each attack: emit to all clients, append to memory, flush to JSON file

### Lifetime Attack Counter
- **D-09:** Cumulative counter stored in same JSON file as attack history
- **D-10:** Counter starts at 0 on first deployment, increments forever
- **D-11:** No reset functionality — counter reflects total attacks since deployment
- **D-12:** Counter persisted immediately with each attack (same write as history)

### Top Analytics (STAT-02, STAT-03)
- **D-13:** Top 5 attacking countries displayed by attack count
- **D-14:** Protocol breakdown: SSH vs Telnet counts
- **D-15:** Port breakdown: Top 5 most-targeted ports
- **D-16:** Real-time incremental aggregation — update counts on each attack
- **D-17:** Aggregations stored in memory and persisted with history JSON
- **D-18:** Recompute aggregations on startup from attack history (fallback)

### UI Layout
- **D-19:** Extend existing StatsPanel component with new sections
- **D-20:** New sections below archetype counters: "Lifetime Attacks", "Top Countries", "Attack Methods"
- **D-21:** LED counter aesthetic maintained (consistent with existing StatsPanel)
- **D-22:** No new panel components — keep single unified stats display

### Claude's Discretion
- Exact JSON file structure (recommend: `{attacks: [], lifetime_count: N, analytics: {...}}`)
- Exact aggregation schema (recommend: `{countries: {US: N, ...}, protocols: {SSH: N, TELNET: N}, ports: {22: N, ...}}`)
- Exact placement of new sections within StatsPanel (recommend: after archetype counters, before scrollable area)
- Error handling for corrupted JSON file (recommend: start fresh, log warning)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Decisions
- `PLAN.md` — Architecture diagram, data model, component specs
- `DESIGN.md` — Design tokens and aesthetic direction
- `.planning/PROJECT.md` — Tech stack, key decisions, aesthetic direction
- `.planning/REQUIREMENTS.md` — Phase 7 requirements: STORE-01 to STORE-03, STAT-01 to STAT-03

### Prior Phases
- `.planning/phases/06-cowrie-integration/06-CONTEXT.md` — CowrieReader, GeoIP service, Socket.io emission
- `.planning/phases/05-docker-containerization/05-CONTEXT.md` — Docker volume patterns, volume sharing
- `.planning/phases/01-foundation/01-CONTEXT.md` — Backend architecture, AttackEvent model
- `.planning/phases/02-core-visualization/02-CONTEXT.md` — StatsPanel LED counter component

### Existing Code
- `backend/main.py` — Socket.io server, `cowrie_emitter()` background task
- `backend/models.py` — AttackEvent Pydantic model
- `frontend/src/components/StatsPanel.tsx` — LED counter display (extend this)
- `frontend/src/lib/socket.ts` — Socket.io client with reconnection logic

</canonical_refs>

<code_context>
## Existing Code Insights

### Backend Structure
- `backend/main.py` — FastAPI + Socket.io server with `cowrie_emitter()` background task
- `backend/models.py` — AttackEvent Pydantic model with all fields needed for storage
- `backend/cowrie_reader.py` — Reads Cowrie logs, classifies archetypes, emits to Socket.io
- `backend/geoip_service.py` — GeoIP lookup for country data
- `backend/requirements.txt` — Python dependencies (may need json module, already standard)

### Frontend Structure
- `frontend/src/components/StatsPanel.tsx` — LED counter component (extend for analytics)
- `frontend/src/lib/socket.ts` — Socket.io client (add history listener)
- `frontend/src/app/page.tsx` — Dashboard page (wire up new events)

### Docker Compose
- `docker-compose.yml` — Backend already mounts volumes (extend with attacks.json volume)
- Backend container has write access to shared volumes (per Phase 5 pattern)

### Integration Points
- New `attack_history` Socket.io event for new connections
- Extend `cowrie_emitter()` to persist after emission
- New in-memory store for last 20 attacks and aggregations
- JSON file read on startup, write after each attack
- Frontend adds `attack_history` event listener on connect

</code_context>

<specifics>
## Specific Ideas

- JSON file location: `/data/attacks.json` (mounted volume, same pattern as Cowrie logs)
- JSON structure: `{attacks: [...], lifetime_count: 423, analytics: {countries: {...}, protocols: {...}, ports: {...}}}`
- History event: `sio.emit('attack_history', [attack_dicts])` on connect
- StatsPanel sections: "Lifetime Attacks" (big number), "Top Countries" (top 5 list), "Attack Methods" (SSH/Telnet counts + top ports)
- Aggregation update: increment counters in memory on each attack, persist with history

</specifics>

<deferred>
## Deferred Ideas

- Historical analysis beyond last 20 attacks — Future
- Attack trends over time (hourly/daily charts) — Future
- Export attack data as CSV — Future
- Multi-honeypot aggregation — Future
- Authentication/authorization — Phase 8

</deferred>

---

*Phase: 07-persistence-analytics*
*Context gathered: 2026-03-26*