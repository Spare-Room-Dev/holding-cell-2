# Phase 5: Docker Containerization — Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

All services run in Docker Compose with proper networking, volume sharing, health checks, and automatic restarts. This phase delivers containerization infrastructure — the foundation for production deployment. Cowrie honeypot runs but with default configuration (OT persona comes in Phase 6). No real attack data processing yet (Phase 6), no persistence yet (Phase 7), no public deployment yet (Phase 8).

</domain>

<decisions>
## Implementation Decisions

### Docker Compose Structure
- **D-01:** Four services: nginx (reverse proxy), frontend (Next.js), backend (FastAPI+Socket.io), cowrie (honeypot)
- **D-02:** Nginx handles all external traffic — routes HTTP/WebSocket to backend, serves frontend static files
- **D-03:** Frontend builds to static files, nginx serves them directly (no Next.js server in production)
- **D-04:** Backend runs on port 8000 internally, nginx proxies to it

### Networking & Security
- **D-05:** Two separate Docker networks: `app-network` (nginx, frontend, backend) and `cowrie-network` (cowrie, backend via volume only)
- **D-06:** Cowrie isolated — cannot reach backend/frontend/nginx via network, only shares volume for logs
- **D-07:** Backend mounts Cowrie log volume as read-only to read attack data
- **D-08:** No network path from Cowrie to app services (per DEPLOY-04)

### Health Checks
- **D-09:** Backend: dedicated `/health` endpoint that returns 200 if FastAPI and Socket.io are running
- **D-10:** Cowrie: process check (`pgrep cowrie`) + port check (`nc -z localhost 2222`)
- **D-11:** Frontend: health check not needed — nginx serves static files, build-time validation
- **D-12:** Nginx: health check not needed — container exits if config invalid
- **D-13:** All services set `restart: unless-stopped` for automatic recovery

### Cowrie Configuration
- **D-14:** Cowrie runs with default configuration in Phase 5 — no OT persona yet
- **D-15:** OT persona customization (motd, filesystem, usernames) deferred to Phase 6
- **D-16:** Cowrie JSON logs written to shared volume at `/var/log/cowrie/`
- **D-17:** Cowrie runs as non-root user inside container (per DEPLOY-04)

### Environment & Secrets
- **D-18:** Configuration via `.env` file at Docker Compose root — ports, volume paths, service names
- **D-19:** No sensitive secrets in Phase 5 — authentication/SSL come in Phase 8
- **D-20:** `.env.example` checked in, actual `.env` gitignored
- **D-21:** Environment variables passed to containers via `env_file` directive

### Claude's Discretion
- Exact Dockerfile structure for each service (follow Docker best practices)
- Exact docker-compose.yml version and syntax (use Compose v3.8+)
- Exact health check intervals and retries (standard values: 30s interval, 3 retries)
- Exact Cowrie image version (use latest stable)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Decisions
- `PLAN.md` — Architecture diagram, data model, API contracts
- `DESIGN.md` — Design tokens and aesthetic direction
- `.planning/PROJECT.md` — Tech stack, key decisions, aesthetic direction
- `.planning/REQUIREMENTS.md` — Phase 5 requirements: DEPLOY-01 to DEPLOY-04

### Prior Phases
- `.planning/phases/01-foundation/01-CONTEXT.md` — Backend architecture, Socket.io setup, dev scripts
- `.planning/phases/02-core-visualization/02-CONTEXT.md` — Frontend components
- `.planning/phases/03-animated-prisoners/03-CONTEXT.md` — Animation patterns
- `.planning/phases/04-polish/04-CONTEXT.md` — Responsive layout, theme toggle

### Docker & Cowrie Documentation
- Docker Compose networking best practices
- Cowrie honeypot configuration reference
- Docker health check syntax

</canonical_refs>

<code_context>
## Existing Code Insights

### Backend Structure
- `backend/main.py` — FastAPI + Socket.io server on port 8000
- `backend/requirements.txt` — Python dependencies
- `backend/archetypes.py` — Archetype classification (Phase 6 will connect to Cowrie)
- `backend/attack_generator.py` — Fake attack generator (Phase 6 replaces with Cowrie reader)
- `backend/models.py` — AttackEvent Pydantic model

### Frontend Structure
- `frontend/` — Next.js 14 App Router
- `frontend/package.json` — Node dependencies
- `frontend/src/lib/socket.ts` — Socket.io client
- `frontend/src/app/page.tsx` — Dashboard page

### Dev Scripts
- Root `package.json` — npm workspaces with `dev:all` script
- Currently runs both services locally without Docker

### Integration Points
- Backend needs new `/health` endpoint for Docker health checks
- Cowrie log volume needs to be mounted read-only to backend
- Nginx config needs WebSocket proxying for Socket.io
- Frontend build output needs to be served by nginx

</code_context>

<specifics>
## Specific Ideas

- Use official Cowrie Docker image or build from source (official image is simpler)
- Nginx config for WebSocket: `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";`
- Health check endpoint: simple `{"status": "ok"}` JSON response, no auth needed
- Cowrie logs in JSON format at `/var/log/cowrie/cowrie.json` — backend will tail this file
- `.env` file: `BACKEND_PORT=8000`, `FRONTEND_PORT=3000`, `COWRIE_SSH_PORT=2222`, `COWRIE_TELNET_PORT=2323`

</specifics>

<deferred>
## Deferred Ideas

- OT persona for Cowrie (mining/industrial theme) — Phase 6
- SSL/HTTPS via Let's Encrypt — Phase 8
- Authentication/authorization — Phase 8
- VPS deployment — Phase 8
- Real attack data processing — Phase 6
- Attack persistence — Phase 7

</deferred>

---

*Phase: 05-docker-containerization*
*Context gathered: 2026-03-26*