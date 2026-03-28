# Project: The Holding Cell

## What This Is

**The Holding Cell** — A gamified SOC/threat intelligence visualization dashboard that renders honeypot attacks as pixel-art "bandits" being thrown into a jail cell.

## Core Value

A visually impressive, working real-time dashboard that demonstrates SOC operations and threat intelligence skills through a distinctive arcade-meets-terminal aesthetic — making threat data feel like an arcade experience without undermining professional credibility.

## Who It's For

Recruiters evaluating a candidate's SOC operations, threat intelligence, and real-time data handling skills.

## Context

This is a **greenfield project**. The PLAN.md and DESIGN.md define Approach A (MVP with fake data) as the starting point:

- **Approach A:** Full visual pipeline (Socket.io → Framer Motion → pixel-art prisoners) with simulated attack data
- **Goal:** Ship a working, visually impressive dashboard in Weekend 1 before introducing real honeypot complexity
- **Weekend 2:** Real Cowrie honeypot integration
- **Weekend 3+:** Additional features (Shodan radar, etc.)

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, python-socketio (async), httpx, uvicorn
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion
- **Ports:** Backend on 8000, Frontend on 3000

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Approach A (fake data) first | Validates dashboard UX before honeypot complexity | Ship Weekend 1 |
| Keep FastAPI + Socket.io | Weekend 2 Cowrie integration is Python-native — better to establish stack now | Established |
| Remove Shodan radar | Not core to app's value | Deferred to Weekend 3 |
| Prisoner entrance animation | Core wow moment — Framer Motion physics with spring | Key differentiator |
| 20-prisoner cell cap | Older ones fade out gracefully | Defined |
| Pixel-art sprites as inline SVG | No external image dependencies, archetype colors via bandana | Implemented Phase 03 |
| Spring physics entrance (300/20) | Bounce physics for new prisoner "wow moment" | Implemented Phase 03 |
| Stiffer shift spring (400/25) | Avoids bounce chaos when grid reflows | Implemented Phase 03 |
| Tailwind responsive breakpoints | md: (768px) and lg: (1024px) align with CONTEXT.md | Implemented Phase 04 |
| Dark mode primary | Default aesthetic is dark terminal, light available via toggle | Implemented Phase 04 |
| Mobile bottom sheet | Framer Motion AnimatePresence with drag-to-dismiss | Implemented Phase 04 |

## Design Direction

- **Aesthetic:** Retro-Futuristic with light pixel-art accents — Bloomberg Terminal meets Hyper Light Drifter
- **Primary accent:** Phosphor Green `#00FF88` (CRT terminal)
- **Typography:** Satoshi Bold (display) + DM Sans (body) + IBM Plex Mono (data)
- **Dark mode primary** — Light mode available as toggle

## Current Milestone: v1.0 Complete — Ready for Deployment

**Goal:** All 8 phases complete. The Holding Cell is ready for VPS deployment with HTTPS, authentication, and firewall security.

**Completed:**
- Phase 01: Foundation — FastAPI backend, Socket.io, fake attack generator
- Phase 02: Core Visualization — JailCellGrid, pixel-art prisoners, stone cell
- Phase 03: Animated Prisoners — Framer Motion entrance, shift spring physics
- Phase 04: Polish — Responsive layout, dark/light mode, mobile bottom sheet
- Phase 05: Docker Containerization — Multi-container setup, health checks
- Phase 06: Cowrie Integration — Real honeypot data, watchfiles log monitoring
- Phase 07: Persistence & Analytics — JSON persistence, attack history, analytics panel
- Phase 08: VPS Deployment & Security — HTTPS, HTTP Basic Auth, UFW firewall, deployment docs

## Requirements

### Active

- [ ] **COW-01**: User can see real SSH/Telnet attacks from Cowrie honeypot in the dashboard
- [ ] **COW-02**: Attack data flows from Cowrie to frontend via Socket.io in real-time
- [ ] **COW-03**: All 5 archetypes classified from real attack fingerprints
- [ ] **DEPLOY-01**: Dashboard accessible via public URL with HTTPS
- [ ] **DEPLOY-02**: Docker Compose orchestrates all services (backend, frontend, Cowrie)
- [ ] **DEPLOY-03**: Services restart automatically on failure
- [ ] **DEPLOY-04**: HTTPS via Let's Encrypt/Certbot with existing domain

### Validated

- [x] Backend: FastAPI + Socket.io server with fake attack generator — Validated in Phase 01
- [x] Frontend: Next.js dashboard with JailCellGrid, Prisoner avatars, StatsPanel — Validated in Phase 01-02
- [x] Real-time: Socket.io connection with auto-reconnect — Validated in Phase 01
- [x] Visual: Pixel-art prisoner sprites with Framer Motion entrance animation — Validated in Phase 03
- [x] Visual: Dark retro-futuristic aesthetic with stone texture cell + iron bars — Validated in Phase 02
- [x] Data: Fake attack generation with realistic country/IP weights and archetype fingerprints — Validated in Phase 01
- [x] Polish: Responsive layout (mobile/tablet/desktop), light/dark mode toggle, mobile bottom sheet — Validated in Phase 04
- [x] Polish: All 5 archetype classifications working per BACK-08 fingerprint rules — Validated in Phase 04
- [x] Polish: Demo-ready MVP with number formatting (commas, 99,999+ cap) — Validated in Phase 04
- [x] Docker: Multi-container orchestration with health checks — Validated in Phase 05
- [x] Cowrie: Real honeypot integration with log monitoring — Validated in Phase 06
- [x] Persistence: JSON file storage with attack history — Validated in Phase 07
- [x] Security: HTTPS, HTTP Basic Auth, UFW firewall — Validated in Phase 08

## Out of Scope

- Real Cowrie honeypot integration (Weekend 2)
- VPS deployment (Weekend 2)
- Shodan radar widget (Weekend 3)
- Docker/Ansible deployment pipeline (Weekend 2+)
- Persistent attacker identity across sessions
- Actual malicious activity storage

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-28 — Milestone v1.0 Complete — Ready for deployment*
