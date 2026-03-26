# Project Research Summary

**Project:** The Holding Cell
**Domain:** SOC / Threat Intelligence Dashboard with Cowrie Honeypot Integration
**Researched:** 2026-03-26
**Confidence:** HIGH

## Executive Summary

The Holding Cell is a real-time security operations center dashboard that visualizes SSH/Telnet attack data from a Cowrie honeypot. The v1.0 (fake data) implementation is complete with a gamified jail-cell metaphor using pixel-art animated prisoners. The next milestone (v1.1) adds real threat intelligence by integrating Cowrie honeypot data, Docker Compose orchestration, and production VPS deployment with HTTPS.

The recommended approach uses a file-watching pattern where the Python backend tails Cowrie's JSON log file via a shared Docker volume, parses events in real-time, and broadcasts them via Socket.io to the Next.js frontend. This architecture avoids network hops between containers while maintaining clean separation of concerns. Docker Compose orchestrates all services (Cowrie, Backend, Frontend, Nginx, Redis) with proper health checks and network isolation.

Key risks center on security: running the honeypot requires strict network segmentation (Cowrie isolated from backend/frontend), proper user isolation (never run as root), and firewall rules to expose only honeypot ports publicly while restricting dashboard access. WebSocket connections behind Nginx require specific configuration to avoid 60-second disconnects. Let's Encrypt rate limits must be respected during testing.

## Key Findings

### Recommended Stack

The existing tech stack (Next.js 14, FastAPI, python-socketio, Tailwind CSS, Framer Motion) is validated and production-ready. New additions for v1.1 include Docker Compose for orchestration, Nginx for reverse proxy with TLS termination, and watchdog/aiofiles for real-time Cowrie log monitoring.

**Core technologies:**
- **Next.js 14 (App Router)**: React framework — App Router is the 2024-2025 standard with server components
- **FastAPI + python-socketio 5.16**: Backend — Native async support pairs well with Cowrie log watching
- **Cowrie (Docker)**: Honeypot — Industry-standard medium-interaction honeypot with JSON output
- **Nginx + Certbot**: Reverse proxy — TLS termination with Let's Encrypt auto-renewal
- **Docker Compose**: Orchestration — Single-command deployment for all services

### Expected Features

**Must have (table stakes) — v1.1 Launch:**
- Real-time attack feed via Socket.io — core value proposition
- Attack count statistics — situational awareness
- Gamified jail cell visualization — core differentiator (COMPLETE in v1.0)
- Connection status indicator — analysts know if feed is live
- HTTPS access — security standard for public apps
- Docker Compose one-command deploy — DevOps competence demonstration

**Should have (competitive):**
- Attacker archetype fingerprinting — educational, shows threat understanding (implemented, needs real data mapping)
- Hover-to-reveal arrest record — detail on demand (COMPLETE in v1.0)
- Real Cowrie honeypot data — live threat intelligence vs. simulated

**Defer (v2+):**
- Geolocation enrichment (MaxMind GeoIP)
- Attack statistics persistence (SQLite/Redis)
- Multi-honeypot aggregation
- Historical analysis / time-series charts

### Architecture Approach

The system uses a dual data source pattern: fake attack generator for development iteration, Cowrie log monitor for production. This allows fast local development without running the honeypot. The file-watching pattern uses watchdog (synchronous) with asyncio bridge to emit Socket.io events without blocking the event loop.

**Major components:**
1. **CowrieLogMonitor** — Tails cowrie.json, parses JSON events, bridges to async Socket.io emission
2. **SocketServer** — Broadcasts attack events to all connected frontend clients (existing)
3. **JailCellGrid** — Visualizes attacker "prisoners" with Framer Motion spring physics (existing)
4. **Nginx** — TLS termination, WebSocket upgrade handling, reverse proxy routing
5. **Docker Networks** — honeypot network (isolated), app network (internal communication)

### Critical Pitfalls

1. **Running Cowrie as root** — Create dedicated `cowrie` user, use `user: "1000:1000"` in Docker Compose
2. **Poor network isolation** — Separate Docker networks for honeypot vs. app, use iptables to block Cowrie outbound
3. **WebSocket drops behind Nginx** — Set `proxy_read_timeout 3600s` and include Upgrade/Connection headers
4. **Let's Encrypt rate limits** — Always use `--staging` for testing; production limit is 5 duplicate certs/week
5. **SSH port conflict** — Move real SSH to alternate port (22022), redirect port 22 to Cowrie via iptables

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Cowrie Integration Setup
**Rationale:** The honeypot is the data source. Must have Cowrie generating real attack data before backend can process it. This phase establishes the foundation for all real threat intelligence.
**Delivers:** Running Cowrie honeypot, Docker volume sharing, backend log watcher, event parsing
**Addresses:** Real Cowrie honeypot data, one-command deploy foundation
**Avoids:** Running Cowrie as root, SSH port conflict, poor network isolation
**Research flag:** STANDARD — well-documented Cowrie Docker setup

### Phase 2: Docker Compose Orchestration
**Rationale:** Production deployment requires coordinating multiple services. Docker Compose manages Cowrie, Backend, Frontend, Nginx, Redis with proper dependency ordering and health checks.
**Delivers:** Complete production stack in docker-compose.yml, health checks, custom networks
**Uses:** Docker Compose, Redis for Socket.IO scaling, health check patterns
**Implements:** Nginx reverse proxy, WebSocket configuration
**Research flag:** STANDARD — common Docker Compose patterns

### Phase 3: VPS Deployment & Security
**Rationale:** Public-facing deployment requires HTTPS, firewall rules, and security hardening. Let's Encrypt setup and Nginx TLS termination are production requirements.
**Delivers:** HTTPS access, firewall rules, dashboard IP restriction, rate limiting
**Uses:** Certbot, Nginx SSL configuration, UFW/iptables
**Avoids:** Exposed dashboard, CORS wildcard, hardcoded secrets
**Research flag:** NEEDS RESEARCH — VPS-specific configurations (DNS setup, provider-specific firewall)

### Phase 4: Real Data Validation
**Rationale:** End-to-end validation that real attacks flow from Cowrie through backend to frontend. Session-based classification logic must be tested with real attack patterns.
**Delivers:** Working production deployment with real threat data, archetype classification from real sessions
**Uses:** Session caching, archetype mapping rules
**Implements:** AttackEvent mapping from Cowrie JSON format
**Research flag:** STANDARD — existing BACK-08 classification rules adapt to real data

### Phase Ordering Rationale

- **Cowrie first (Phase 1)** because no real data flows without the honeypot running. The Docker volume and log access patterns must be established before backend integration.
- **Docker Compose second (Phase 2)** because it orchestrates all services together. Health checks and network configuration must be in place before production deployment.
- **VPS Security third (Phase 3)** because HTTPS and firewall rules require a working stack first. Security without a working application is premature.
- **Validation last (Phase 4)** because real data validation requires all components working in production.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (VPS Deployment):** Domain DNS configuration is provider-specific; Certbot renewal hooks need testing; VPS provider may have specific firewall interfaces (AWS Security Groups vs. DigitalOcean UFW).

Phases with standard patterns (skip research-phase):
- **Phase 1 (Cowrie Integration):** Well-documented Docker setup, official cowrie/cowrie image, established log format.
- **Phase 2 (Docker Compose):** Common patterns for multi-service orchestration, health checks are standard Docker feature.
- **Phase 4 (Validation):** Uses existing classification rules (BACK-08), Cowrie event format is documented.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified via PyPI, Docker Hub, official documentation (Mar 2026) |
| Features | HIGH | Clear table stakes vs differentiators, competitor analysis completed |
| Architecture | HIGH | Official Cowrie docs, Socket.IO docs, Docker patterns well-established |
| Pitfalls | HIGH | Official Microsoft Sentinel integration guide, Socket.IO troubleshooting docs, recent security analysis |

**Overall confidence:** HIGH

### Gaps to Address

- **Domain configuration:** DNS setup varies by registrar; needs VPS-specific planning during Phase 3
- **VPS provider firewall:** AWS Security Groups vs. DigitalOcean UFW vs. Hetzner firewall — specific to chosen provider
- **Cowrie user database:** Default credentials vs. custom userdb.txt configuration — needs decision during Phase 1
- **Certbot auto-renewal:** Systemd timer vs. Docker sidecar vs. cron — needs selection during Phase 3

## Sources

### Primary (HIGH confidence)
- [PyPI] python-socketio 5.16.1, FastAPI 0.135.2 — verified Mar 2026
- [Docker Hub] cowrie/cowrie:latest — official Cowrie image
- [Official Docs] Cowrie Output Events — https://docs.cowrie.org/en/latest/OUTPUT.html
- [Official Docs] Cowrie Docker — https://docs.cowrie.org/en/latest/DOCKER.html
- [Official Docs] Socket.IO Redis Adapter — https://socket.io/docs/v4/redis-adapter
- [Microsoft Sentinel] Cowrie Integration Guide — https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/cowrie-honeypot-and-its-integration-with-microsoft-sentinel/ba-p/4258349

### Secondary (MEDIUM confidence)
- [Better Stack] FastAPI Docker Best Practices — production deployment patterns
- [Medium] FastAPI + Socket.IO Integration — ASGIApp wrapper pattern
- [PhoenixNAP] Let's Encrypt Nginx Guide — HTTPS configuration
- [AmbientNode] Running a Cowrie Honeypot: Data and Findings — real attack statistics

### Tertiary (LOW confidence — needs validation during implementation)
- Community Docker Compose examples — verify against current best practices
- Blog tutorials for Nginx WebSocket — test with actual Socket.IO client

---
*Research completed: 2026-03-26*
*Ready for roadmap: yes*