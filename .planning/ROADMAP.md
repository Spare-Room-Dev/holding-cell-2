# Roadmap: The Holding Cell

## Overview

A gamified SOC/threat intelligence visualization dashboard that renders honeypot attacks as pixel-art "bandits" being thrown into a jail cell. **v1.0 (Phases 1-4)** delivered the fake-data MVP with animated prisoners. **v1.1 (Phases 5-8)** adds real threat intelligence with Cowrie honeypot integration, Docker Compose deployment, and production VPS hosting.

---

## v1.0 Complete (Phases 1-4)

- [x] **Phase 1: Foundation** - Backend server, fake attack generator, Socket.io real-time pipeline, dev experience
- [x] **Phase 2: Core Visualization** - JailCellGrid with stone texture + iron bars, StatsPanel with LED counters
- [x] **Phase 3: Animated Prisoners** - Pixel-art sprites with spring entrance animation, ArrestRecord tooltip on hover
- [x] **Phase 4: Polish** - Responsive layout, archetype classification end-to-end, demo-ready

---

## v1.1 Real Threats (Phases 5-8)

- [x] **Phase 5: Docker Containerization** - Docker Compose orchestrates all services with health checks and volume sharing
- [x] **Phase 6: Cowrie Integration** - Real SSH/Telnet attack data flows from Cowrie honeypot to dashboard
- [ ] **Phase 7: Persistence & Analytics** - Last 20 attacks stored, lifetime stats, and top attack analytics
- [ ] **Phase 8: VPS Deployment & Security** - Public HTTPS access with authentication, firewall, and network isolation

## Phase Details

### Phase 5: Docker Containerization
**Goal**: All services run in Docker Compose with proper networking, volume sharing, and automatic restarts
**Depends on**: Phase 4 (v1.0 complete)
**Requirements**: DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04
**Success Criteria** (what must be TRUE):
  1. User can run `docker compose up` and all services start (Cowrie, Backend, Frontend, Nginx)
  2. Cowrie JSON logs are readable by backend via shared Docker volume
  3. Services restart automatically when they fail (health checks configured)
  4. Cowrie runs as non-root user with network isolation from app services
**Plans**: 2 plans
- [x] 05-01-PLAN.md — Create Dockerfiles for backend/frontend and nginx config with WebSocket proxy
- [x] 05-02-PLAN.md — Create docker-compose.yml with 4 services, 2 networks, named volumes, health checks

### Phase 6: Cowrie Integration
**Goal**: Real SSH/Telnet attacks flow from Cowrie honeypot to frontend dashboard in real-time
**Depends on**: Phase 5
**Requirements**: COW-01, COW-02, COW-03, COW-04, COW-05
**Success Criteria** (what must be TRUE):
  1. Cowrie honeypot runs with mining/industrial OT persona (motd, filesystem, usernames reflect OT environment)
  2. Real SSH/Telnet attacks appear in dashboard with correct archetype classification
  3. Session events are correlated (connect, login, commands, close) by session ID
  4. All 5 archetypes classified correctly from real attack fingerprints (HASSH + command patterns)
  5. GeoIP country data displays correctly for attacker IP addresses
**Plans**: 3 plans
- [x] 06-01-PLAN.md — Cowrie OT persona config + GeoIP database mount setup
- [x] 06-02-PLAN.md — Cowrie reader module with session correlation + classification
- [x] 06-03-PLAN.md — Backend integration, disable fake generator, wire real data flow

### Phase 7: Persistence & Analytics
**Goal**: All visitors see the same attack history with lifetime stats and top attack analytics
**Depends on**: Phase 6
**Requirements**: STORE-01, STORE-02, STORE-03, STAT-01, STAT-02, STAT-03
**Success Criteria** (what must be TRUE):
  1. Last 20 attacks stored persistently (survives server restart)
  2. All connected visitors see identical attack history at any moment
  3. New visitor connects and immediately sees the last 20 attacks on page load
  4. Lifetime attack counter shows total attacks since deployment
  5. Top attacking locations displayed (countries by attack count)
  6. Top attack methods displayed (SSH vs Telnet, ports targeted)
**Plans**: 2 plans
- [ ] 07-01-PLAN.md — Backend persistence with JSON storage, history event on connect, atomic writes
- [ ] 07-02-PLAN.md — Frontend analytics UI with CountryList, MethodsPanel, extended StatsPanel

### Phase 8: VPS Deployment & Security
**Goal**: Dashboard accessible publicly via HTTPS with proper authentication and network security
**Depends on**: Phase 7
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06
**Success Criteria** (what must be TRUE):
  1. Dashboard accessible via public HTTPS URL with valid Let's Encrypt certificate
  2. Dashboard protected with authentication (password or IP whitelist)
  3. WebSocket connections stay alive without 60-second disconnects (Nginx configured correctly)
  4. Firewall exposes only: honeypot ports (22, 23), HTTPS (443), admin SSH (alternate port)
  5. No hardcoded secrets; all sensitive config via environment files
  6. Cowrie network isolated from app network (honeypot cannot reach backend/frontend)
**Plans**: 3 plans (Wave 1: 08-01, 08-03 | Wave 2: 08-02)
- [ ] 08-01-PLAN.md — Create nginx.prod.conf with SSL termination, docker-compose.prod.yml, certbot systemd timer (SEC-02, SEC-03, SEC-05)
- [ ] 08-02-PLAN.md — Add HTTP Basic Auth to nginx, create htpasswd setup script, update .env.example (SEC-01, SEC-05)
- [ ] 08-03-PLAN.md — Create UFW firewall script, verify network isolation, create deployment documentation (SEC-04, SEC-06)

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2026-03-24 |
| 2. Core Visualization | 3/3 | Complete | 2026-03-25 |
| 3. Animated Prisoners | 2/2 | Complete | 2026-03-25 |
| 4. Polish | 0/3 | In Progress | - |
| 5. Docker Containerization | 2/2 | Complete | 2026-03-26 |
| 6. Cowrie Integration | 3/3 | Complete | 2026-03-26 |
| 7. Persistence Layer | 0/2 | Not started | - |
| 8. VPS Deployment & Security | 0/3 | Planned | - |

---

*Roadmap created: 2026-03-24*
*v1.1 Real Threats added: 2026-03-26*
*Phase 5 planned: 2026-03-26*
*Phase 6 planned: 2026-03-26*
*Phase 7 planned: 2026-03-26*
*Phase 8 planned: 2026-03-28*
*Granularity: coarse (4 phases per milestone)*
*Coverage: 20/20 v1.1 requirements mapped*