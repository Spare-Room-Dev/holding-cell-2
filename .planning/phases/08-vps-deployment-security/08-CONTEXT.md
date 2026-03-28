# Phase 8: VPS Deployment & Security — Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Dashboard accessible publicly via HTTPS with authentication and network security. This phase takes the Docker Compose setup from Phases 5-7 and makes it production-ready on a VPS. HTTPS via Let's Encrypt, HTTP Basic Auth for access control, UFW firewall, and proper port exposure. No new features — this phase is purely deployment and security hardening.

</domain>

<decisions>
## Implementation Decisions

### Authentication
- **D-01:** HTTP Basic Auth — username/password in nginx htpasswd file
- **D-02:** htpasswd file stored outside repo (e.g., `/etc/nginx/.htpasswd`)
- **D-03:** Single admin user for initial deployment (can add users later)
- **D-04:** Password stored in `.env` file on server, referenced in nginx config

### HTTPS & Certificates
- **D-05:** Certbot standalone mode for Let's Encrypt certificates
- **D-06:** systemd timer for certificate renewal (runs twice daily)
- **D-07:** HTTP redirect to HTTPS — no unencrypted access
- **D-08:** Certificate directory mounted to nginx container for SSL termination

### Firewall & Ports
- **D-09:** UFW (Uncomplicated Firewall) for port management
- **D-10:** Admin SSH on port 2244 (alternate port to avoid Cowrie honeypot conflict)
- **D-11:** Cowrie honeypot ports 22 and 23 publicly accessible — maximum attack visibility
- **D-12:** HTTPS port 443 exposed for dashboard access
- **D-13:** Port 80 exposed for Let's Encrypt ACME challenges (redirects to HTTPS after)
- **D-14:** All other ports closed by default

### Network Architecture
- **D-15:** Cowrie on isolated `cowrie-network` (per Phase 5 D-05, D-06)
- **D-16:** Backend only accesses Cowrie logs via shared volume (per Phase 5 D-07)
- **D-17:** Nginx terminates SSL, proxies to backend on internal network

### Deployment Process
- **D-18:** Manual deployment: SSH + git pull + docker compose up
- **D-19:** `.env` file on server contains all secrets (gitignored)
- **D-20:** `.env.example` checked in as template (already exists from Phase 5)
- **D-21:** No CI/CD automation — simple manual process for portfolio demo

### Monitoring & Logging
- **D-22:** Log viewing only: `docker compose logs` and `journalctl`
- **D-23:** No additional monitoring infrastructure (Prometheus/Grafana overkill for portfolio)
- **D-24:** Docker container logs accessible via `docker logs <container>`

### Claude's Discretion
- Exact htpasswd file location and permissions
- Exact UFW rules syntax and order
- Exact systemd timer unit file for certbot renewal
- Exact nginx SSL configuration for HTTPS
- Docker Compose production override file structure

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 8 requirements: SEC-01 to SEC-06

### Prior Phases
- `.planning/phases/05-docker-containerization/05-CONTEXT.md` — Docker Compose structure, nginx config, volume sharing
- `.planning/phases/06-cowrie-integration/06-CONTEXT.md` — Cowrie reader, GeoIP, Socket.io emission
- `.planning/phases/07-persistence-analytics/07-CONTEXT.md` — Attack history persistence, analytics

### Architecture Documents
- `PLAN.md` — Architecture diagram, data model
- `DESIGN.md` — Design tokens and aesthetic direction
- `.planning/PROJECT.md` — Tech stack, key decisions

### Existing Infrastructure
- `docker-compose.yml` — Docker Compose orchestration (needs production modifications)
- `nginx/nginx.conf` — Current nginx config (needs SSL and auth additions)
- `.env.example` — Environment template (needs production values)

</canonical_refs>

<code_context>
## Existing Code Insights

### Docker Compose Structure
- `docker-compose.yml` — Four services: nginx, frontend, backend, cowrie
- Networks: `app-network` (nginx/frontend/backend), `cowrie-network` (isolated)
- Volumes: `frontend-static`, `cowrie-logs`, `persistence-data`
- All services have `restart: unless-stopped`

### Nginx Configuration
- `nginx/nginx.conf` — Reverse proxy with WebSocket support
- Already has 24-hour WebSocket timeouts (per Phase 5 D-12)
- Currently serves HTTP on port 80 — needs SSL termination
- Missing: SSL configuration, htpasswd auth, HTTP redirect

### Backend Health Check
- `backend/main.py` — Has `/health` endpoint at line 100+ (per Phase 5 D-09)
- Health check used in Docker Compose for service readiness

### Current Port Mapping
- Port 80 (HTTP) → nginx
- Port 2222 → Cowrie SSH honeypot
- Port 2323 → Cowrie Telnet honeypot
- Port 8000 → Backend (internal only, not exposed externally)

### Integration Points
- Nginx needs SSL certificate mount and htpasswd auth
- Docker Compose needs production override for SSL volume
- UFW rules need to allow: 22 (SSH honeypot), 23 (Telnet honeypot), 443 (HTTPS), 2244 (admin SSH), 80 (HTTP redirect)
- Certbot needs standalone mode to obtain certificates before nginx starts

</code_context>

<specifics>
## Specific Ideas

- htpasswd file at `/etc/nginx/.htpasswd` owned by root:nginx with 640 permissions
- Certbot systemd timer: `certbot.timer` runs `certbot renew` twice daily
- UFW rules: allow 2244/tcp (admin SSH), 22/tcp (honeypot), 23/tcp (honeypot), 80/tcp (ACME), 443/tcp (HTTPS)
- Docker Compose production override: `docker-compose.prod.yml` with SSL volume and env file path
- Nginx SSL config: `listen 443 ssl; ssl_certificate /etc/letsencrypt/live/DOMAIN/fullchain.pem;`
- HTTP redirect: `server { listen 80; return 301 https://$host$request_uri; }`

</specifics>

<deferred>
## Deferred Ideas

- Multi-user authentication system — Future
- OAuth/SSO integration — Future
- Backup/restore automation — Future
- Monitoring dashboards (Grafana) — Future
- Log aggregation (Dozzle, Loki) — Future
- Rate limiting — Future (could add nginx rate limiting)
- Fail2ban for brute force protection — Future

</deferred>

---

*Phase: 08-vps-deployment-security*
*Context gathered: 2026-03-28*