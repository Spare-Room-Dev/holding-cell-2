# Phase 5: Docker Containerization — Discussion Log

**Date:** 2026-03-26

## Discussion Flow

### 1. Docker Compose Structure

**Question:** How many services should Docker Compose manage?

| Option | Description |
|--------|-------------|
| 4-service (nginx, frontend, backend, cowrie) (recommended) | Clean separation: nginx handles all external traffic, frontend serves static files via nginx, backend API proxied through nginx. Standard production pattern, easier SSL management. |
| 3-service (backend+frontend combined, cowrie, optional nginx) | Fewer containers to manage. Backend serves frontend static files directly, no separate nginx container. Simpler dev setup but harder SSL/caching later. |

**Selected:** 4-service (nginx, frontend, backend, cowrie)

**Rationale:** Standard production pattern with nginx as reverse proxy. Clean separation of concerns. Easier SSL management in Phase 8.

---

### 2. Networking

**Question:** How should networks be structured for security?

| Option | Description |
|--------|-------------|
| Two networks (isolated cowrie) (recommended) | Cowrie isolated on separate network, app services (backend+frontend+nginx) on another. Cowrie can only talk to backend via shared volume, not via network. More secure, satisfies DEPLOY-04. |
| Single network with restrictions | All services on one network with firewall rules. Simpler but less secure — Cowrie could theoretically reach other services if compromised. |

**Selected:** Two networks (isolated cowrie)

**Rationale:** Satisfies DEPLOY-04 (Cowrie network isolation). Cowrie cannot reach backend/frontend/nginx via network — only shares log volume.

---

### 3. Backend Health Check

**Question:** What health check should Backend have?

| Option | Description |
|--------|-------------|
| /docs endpoint health | Use FastAPI's /docs endpoint for health. Simple but exposes API documentation in production. |
| Dedicated /health endpoint (recommended) | Add a dedicated /health endpoint in FastAPI that checks Socket.io is running. Best practice, no docs exposure. |
| No health check (process-only restart) | No health check for backend — let it restart unconditionally. Simpler but slower recovery on failure. |

**Selected:** Dedicated /health endpoint

**Rationale:** Best practice for production. No docs exposure. Can verify Socket.io is running.

---

### 4. Cowrie Health Check

**Question:** What health check should Cowrie honeypot have?

| Option | Description |
|--------|-------------|
| Process + port check (recommended) | Check if Cowrie process is running and port 2222 is listening. Doesn't verify honeypot logic, but sufficient for Phase 5. |
| Active SSH connection test | Actually SSH connect and disconnect. Validates honeypot is accepting connections but adds complexity. |
| No health check (process-only restart) | No health check — Cowrie restarts only on crash. Simpler but less reliable. |

**Selected:** Process + port check

**Rationale:** Sufficient for Phase 5. Validates service is running without over-engineering.

---

### 5. Cowrie Configuration Scope

**Question:** How much Cowrie persona setup in Phase 5?

| Option | Description |
|--------|-------------|
| Default config now, OT persona in Phase 6 (recommended) | Just get Cowrie running in Docker with default config. OT persona (motd, filesystem, usernames) comes in Phase 6. Focus on containerization basics this phase. |
| Full OT persona now | Set up mining/industrial OT persona now (motd, fake filesystem). More work but Phase 6 will have less to do. |

**Selected:** Default config now, OT persona in Phase 6

**Rationale:** Phase 5 scope is containerization. OT persona is content work for Phase 6.

---

### 6. Environment & Secrets

**Question:** How should environment configuration be handled?

| Option | Description |
|--------|-------------|
| .env files for config, no secrets yet (recommended) | Use .env files for configuration (ports, volume paths). Sensitive secrets (if any) can come in Phase 8. Simple and standard for Docker Compose. |
| Prepare for secrets now | Set up Docker secrets or .env with secret placeholders now, ready for Phase 8 security. More upfront work but better prepared. |

**Selected:** .env files for config, no secrets yet

**Rationale:** Simple and standard. No sensitive secrets needed in Phase 5. Phase 8 will handle authentication/SSL.

---

## Summary of Decisions

| Area | Decision |
|------|----------|
| Docker Compose Structure | 4 services: nginx, frontend, backend, cowrie |
| Networking | Two isolated networks (app-network, cowrie-network) |
| Backend Health | Dedicated /health endpoint |
| Cowrie Health | Process check + port 2222 check |
| Cowrie Scope | Default config now, OT persona in Phase 6 |
| Environment | .env files for config, no secrets yet |

---

*Discussion completed: 2026-03-26*