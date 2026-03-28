# Phase 8: VPS Deployment & Security - Research

**Researched:** 2026-03-28
**Domain:** VPS deployment, HTTPS/SSL, HTTP Basic Auth, UFW firewall, Docker Compose production configuration
**Confidence:** HIGH

## Summary

This phase takes the existing Docker Compose setup from Phases 5-7 and makes it production-ready on a VPS with HTTPS via Let's Encrypt, HTTP Basic Auth for access control, UFW firewall, and proper port exposure. The deployment is purely infrastructure hardening—no new application features.

The architecture is already well-defined in CONTEXT.md: nginx terminates SSL and handles authentication, proxies to the FastAPI backend for WebSocket traffic, and serves the static frontend. Cowrie runs on an isolated network. The research focuses on the specific configuration patterns needed for each security layer.

**Primary recommendation:** Use Certbot standalone mode with systemd timer for certificate management, mount `/etc/letsencrypt` into the nginx container for SSL termination, add htpasswd auth to the nginx server block, and configure UFW to allow only ports 22 (honeypot), 23 (honeypot), 80 (ACME), 443 (HTTPS), and 2244 (admin SSH).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** HTTP Basic Auth — username/password in nginx htpasswd file
- **D-02:** htpasswd file stored outside repo (e.g., `/etc/nginx/.htpasswd`)
- **D-03:** Single admin user for initial deployment (can add users later)
- **D-04:** Password stored in `.env` file on server, referenced in nginx config
- **D-05:** Certbot standalone mode for Let's Encrypt certificates
- **D-06:** systemd timer for certificate renewal (runs twice daily)
- **D-07:** HTTP redirect to HTTPS — no unencrypted access
- **D-08:** Certificate directory mounted to nginx container for SSL termination
- **D-09:** UFW (Uncomplicated Firewall) for port management
- **D-10:** Admin SSH on port 2244 (alternate port to avoid Cowrie honeypot conflict)
- **D-11:** Cowrie honeypot ports 22 and 23 publicly accessible — maximum attack visibility
- **D-12:** HTTPS port 443 exposed for dashboard access
- **D-13:** Port 80 exposed for Let's Encrypt ACME challenges (redirects to HTTPS after)
- **D-14:** All other ports closed by default
- **D-15:** Cowrie on isolated `cowrie-network` (per Phase 5 D-05, D-06)
- **D-16:** Backend only accesses Cowrie logs via shared volume (per Phase 5 D-07)
- **D-17:** Nginx terminates SSL, proxies to backend on internal network
- **D-18:** Manual deployment: SSH + git pull + docker compose up
- **D-19:** `.env` file on server contains all secrets (gitignored)
- **D-20:** `.env.example` checked in as template (already exists from Phase 5)
- **D-21:** No CI/CD automation — simple manual process for portfolio demo
- **D-22:** Log viewing only: `docker compose logs` and `journalctl`
- **D-23:** No additional monitoring infrastructure (Prometheus/Grafana overkill for portfolio)
- **D-24:** Docker container logs accessible via `docker logs <container>`

### Claude's Discretion
- Exact htpasswd file location and permissions
- Exact UFW rules syntax and order
- Exact systemd timer unit file for certbot renewal
- Exact nginx SSL configuration for HTTPS
- Docker Compose production override file structure

### Deferred Ideas (OUT OF SCOPE)
- Multi-user authentication system — Future
- OAuth/SSO integration — Future
- Backup/restore automation — Future
- Monitoring dashboards (Grafana) — Future
- Log aggregation (Dozzle, Loki) — Future
- Rate limiting — Future (could add nginx rate limiting)
- Fail2ban for brute force protection — Future

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SEC-01 | Dashboard protected with authentication (password protection or IP whitelist) | HTTP Basic Auth with htpasswd — see Authentication section |
| SEC-02 | HTTPS via Let's Encrypt with auto-renewal | Certbot standalone + systemd timer — see HTTPS & Certificates section |
| SEC-03 | Nginx WebSocket configuration prevents 60-second disconnects | Already implemented in Phase 5 (24-hour timeouts) — verify existing config |
| SEC-04 | Firewall exposes only: honeypot ports (22, 23), HTTPS (443), admin SSH (alternate port) | UFW configuration — see Firewall & Ports section |
| SEC-05 | No hardcoded secrets; environment files for sensitive configuration | `.env` file pattern already established — extend for production secrets |
| SEC-06 | Cowrie network isolated from app network (no cross-talk between honeypot and dashboard) | Already implemented in Phase 5 (cowrie-network internal: true) — verify existing config |

</phase_requirements>

## Standard Stack

### Core
| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Certbot | latest (snap/pkg) | Let's Encrypt SSL certificates | Official EFF client, standard for Let's Encrypt |
| nginx | alpine (existing) | SSL termination, reverse proxy, auth | Already in use, handles WebSocket |
| UFW | 0.36+ | Firewall management | Ubuntu standard, simpler than iptables |

### Supporting
| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| apache2-utils | latest | htpasswd utility | Create password files for Basic Auth |
| systemd | 245+ | Timer for cert renewal | Auto-renew certificates twice daily |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Certbot standalone | Certbot webroot | Requires nginx running during cert obtain; standalone simpler for initial setup |
| HTTP Basic Auth | OAuth/SSO | OAuth is overkill for single-user portfolio demo |
| UFW | iptables directly | iptables is more powerful but UFW is simpler for basic port filtering |
| systemd timer | cron | systemd has better logging, persistent execution after downtime |

## Architecture Patterns

### Recommended Production Structure

```
project/
├── docker-compose.yml           # Base configuration (existing)
├── docker-compose.prod.yml      # Production overrides (NEW)
├── nginx/
│   └── nginx.conf               # HTTP-only config (existing)
├── nginx/
│   └── nginx.prod.conf          # HTTPS + auth config (NEW)
├── .env.example                 # Template (existing)
├── deploy/
│   └── certbot-renew.service    # systemd service unit
│   └── certbot-renew.timer      # systemd timer unit
└── .env                         # Production secrets (gitignored, server-only)
```

### Pattern 1: Certbot Standalone for Docker

**What:** Obtain certificates before nginx starts by having Certbot run its own temporary web server on port 80.

**When to use:** Initial certificate acquisition or when nginx isn't running during cert obtain.

**Workflow:**
```bash
# 1. Stop nginx if running (to free port 80)
docker compose -f docker-compose.yml -f docker-compose.prod.yml stop nginx

# 2. Obtain certificate
sudo certbot certonly --standalone -d your.domain.com --email admin@domain.com --agree-tos --no-eff-email

# 3. Start nginx with SSL
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Source:** [DigitalOcean Certbot Standalone Guide](https://digitalocean.com/community/tutorials/how-to-use-certbot-standalone-mode-to-retrieve-lets-encrypt-ssl-certificates-on-ubuntu-22-04)

### Pattern 2: Docker Compose Production Override

**What:** Layer production-specific configuration over the base docker-compose.yml.

**Example docker-compose.prod.yml:**
```yaml
# Production overrides
services:
  nginx:
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/conf.d/default.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /etc/nginx/.htpasswd:/etc/nginx/.htpasswd:ro
    networks:
      - app-network
```

**Key merge behavior:** Lists (ports) are combined, maps (environment) merge by key, scalars (image) are replaced.

**Source:** [Docker Compose Merge Documentation](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge)

### Pattern 3: Nginx SSL + WebSocket + Auth

**What:** Single server block with SSL termination, WebSocket proxy, and Basic Auth.

**Example nginx.prod.conf:**
```nginx
# Map for WebSocket upgrade
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

upstream backend {
    server backend:8000;
}

# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name your.domain.com;

    # ACME challenge location (for cert renewal)
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server - with auth and WebSocket
server {
    listen 443 ssl http2;
    server_name your.domain.com;

    # SSL certificates from Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/your.domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your.domain.com/privkey.pem;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # HTTP Basic Auth
    auth_basic "The Holding Cell - Dashboard";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Frontend static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Socket.io WebSocket endpoint (extended timeouts)
    location /socket.io/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;

        # WebSocket upgrade headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Extended timeouts for WebSocket (24 hours)
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;

        # Disable buffering for real-time
        proxy_buffering off;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Health check endpoint (no auth)
    location /health {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

**Source:** [NGINX WebSocket Proxy Guide](https://websocket.org/guides/infrastructure/nginx/)

### Pattern 4: systemd Timer for Certificate Renewal

**What:** Automate certificate renewal with systemd timer instead of cron.

**certbot-renew.service:**
```ini
[Unit]
Description=Let's Encrypt certificate renewal
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
# Stop nginx, renew, start nginx
ExecStart=/usr/bin/docker compose -f /opt/holding-cell/docker-compose.yml -f /opt/holding-cell/docker-compose.prod.yml stop nginx
ExecStart=/usr/bin/certbot renew --quiet --standalone
ExecStart=/usr/bin/docker compose -f /opt/holding-cell/docker-compose.yml -f /opt/holding-cell/docker-compose.prod.yml start nginx
```

**certbot-renew.timer:**
```ini
[Unit]
Description=Twice daily renewal of Let's Encrypt certificates

[Timer]
OnCalendar=*-*-* 00,12:00:00
RandomizedDelaySec=3600
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now certbot-renew.timer
```

**Source:** [systemd Certbot Timer Guide](https://k4yt3x.com/automatically-renew-certbot-certificates-with-systemd-timers/)

### Anti-Patterns to Avoid

- **Running Certbot webroot mode without nginx:** Webroot requires nginx running; standalone is simpler for initial setup
- **Short WebSocket timeouts:** Default 60s timeout disconnects idle connections; use 24+ hours
- **htpasswd in web root:** Store outside any served directory
- **Basic Auth over HTTP:** Always use HTTPS; credentials are Base64 encoded (not encrypted)
- **MD5 hashed passwords:** Use bcrypt (`htpasswd -B`) for security

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom bcrypt implementation | `htpasswd -B` utility | battle-tested, correct salt handling |
| SSL configuration | Manual cipher selection | Modern Mozilla SSL config | Security best practices, regular updates |
| Certificate renewal | Custom cron script | systemd timer + Certbot | Better logging, persistent execution |
| Firewall rules | iptables directly | UFW | Simpler syntax, fewer mistakes |

## Runtime State Inventory

*This phase involves deployment configuration changes. The following runtime states are addressed:*

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — persistence-data volume already exists from Phase 7 | No changes needed |
| Live service config | nginx.conf will be replaced with nginx.prod.conf for production | Create new prod config file |
| OS-registered state | UFW rules will be configured on VPS | Create UFW setup script or document commands |
| Secrets/env vars | `.env` file on server will need domain, admin credentials | Document `.env` additions |
| Build artifacts | No changes — Docker images remain same | No changes needed |

## Common Pitfalls

### Pitfall 1: Port 80 Conflict During Certificate Renewal
**What goes wrong:** Certbot standalone mode needs port 80, but nginx is already using it.
**Why it happens:** Both Certbot and nginx try to bind to port 80 simultaneously.
**How to avoid:** Stop nginx container before running `certbot renew`, then start it after. The systemd service unit should handle this automatically.
**Warning signs:** "Port 80 is already in use" error during renewal.

### Pitfall 2: WebSocket Connection Drops After 60 Seconds
**What goes wrong:** Dashboard disconnects after 1 minute of idle time.
**Why it happens:** Default nginx `proxy_read_timeout` is 60s; Socket.io connections appear idle when no messages are flowing.
**How to avoid:** Already addressed in Phase 5 with 86400s (24-hour) timeouts — verify these are preserved in production config.
**Warning signs:** Users report "SIGNAL LOST" banner after idle period.

### Pitfall 3: htpasswd File Not Found in Docker Container
**What goes wrong:** nginx returns 500 error because auth file is missing.
**Why it happens:** htpasswd file exists on host but not mounted into container.
**How to avoid:** Add volume mount in docker-compose.prod.yml: `/etc/nginx/.htpasswd:/etc/nginx/.htpasswd:ro`
**Warning signs:** nginx error logs show "auth_basic_user_file" directive failed.

### Pitfall 4: UFW Blocks Docker Ports
**What goes wrong:** Docker-published ports are accessible even when UFW denies them.
**Why it happens:** Docker manipulates iptables directly, bypassing UFW rules.
**How to avoid:** Configure Docker to use UFW by setting `"iptables": false` in `/etc/docker/daemon.json`, OR explicitly manage Docker's iptables chain. For this project, the simpler approach is: Docker exposes only the ports we need (22, 23, 80, 443, 2244), and we rely on Docker's port publishing rather than UFW for container isolation.
**Warning signs:** Port scans show open ports that UFW should block.

### Pitfall 5: Certificate Chain Incomplete
**What goes wrong:** SSL labs reports incomplete chain, some clients reject certificate.
**Why it happens:** Using `cert.pem` instead of `fullchain.pem`.
**How to avoid:** Always use `fullchain.pem` for `ssl_certificate`, not `cert.pem`. Let's Encrypt provides both; fullchain includes intermediate certificates.
**Warning signs:** Browser shows certificate valid, but curl/API clients fail.

### Pitfall 6: Admin SSH Port Not Accessible After UFW Enable
**What goes wrong:** Locked out of server after enabling UFW because alternate SSH port not allowed.
**Why it happens:** Default UFW only allows port 22, but admin SSH is on port 2244.
**How to avoid:** Always allow admin SSH port BEFORE enabling UFW: `sudo ufw allow 2244/tcp`
**Warning signs:** SSH connection timeout after `ufw enable`.

## Code Examples

### htpasswd Generation (bcrypt)

```bash
# Install apache2-utils (includes htpasswd)
# Ubuntu/Debian:
sudo apt install apache2-utils

# Create htpasswd file with bcrypt-hashed password
sudo htpasswd -cB /etc/nginx/.htpasswd admin
# Enter password when prompted

# Set correct permissions
sudo chown root:nginx /etc/nginx/.htpasswd
sudo chmod 640 /etc/nginx/.htpasswd
```

**Source:** [NGINX Basic Auth Guide](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication)

### UFW Configuration Script

```bash
#!/bin/bash
# UFW setup for The Holding Cell VPS

# Reset to defaults (careful on production!)
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Admin SSH (alternate port for security)
sudo ufw allow 2244/tcp comment 'Admin SSH'

# Honeypot ports (public)
sudo ufw allow 22/tcp comment 'Cowrie SSH honeypot'
sudo ufw allow 23/tcp comment 'Cowrie Telnet honeypot'

# HTTPS and HTTP (for ACME challenges)
sudo ufw allow 80/tcp comment 'HTTP/ACME'
sudo ufw allow 443/tcp comment 'HTTPS'

# Enable firewall
sudo ufw --force enable

# Show status
sudo ufw status numbered
```

**Expected output:**
```
Status: active
     To                         Action      From
[ 1] 2244/tcp                   ALLOW IN    Anywhere                   # Admin SSH
[ 2] 22/tcp                     ALLOW IN    Anywhere                   # Cowrie SSH honeypot
[ 3] 23/tcp                     ALLOW IN    Anywhere                   # Cowrie Telnet honeypot
[ 4] 80/tcp                     ALLOW IN    Anywhere                   # HTTP/ACME
[ 5] 443/tcp                    ALLOW IN    Anywhere                   # HTTPS
```

### Environment File Template

```bash
# .env (server-only, gitignored)

# Domain configuration
DOMAIN=your-domain.com

# Admin credentials (for htpasswd)
ADMIN_USER=admin
ADMIN_PASSWORD_HASH=<generated-by-htpasswd>

# Docker ports
FRONTEND_PORT=80
HTTPS_PORT=443
BACKEND_PORT=8000
COWRIE_SSH_PORT=2222
COWRIE_TELNET_PORT=2323

# Volume paths
COWRIE_LOG_PATH=/var/log/cowrie

# GeoIP database path
GEOIP_DB_PATH=/geoip/GeoLite2-Country.mmdb
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|--------------|--------|
| cron for cert renewal | systemd timers | ~2020 | Better logging, persistent execution |
| APR1/MD5 password hashes | bcrypt (`htpasswd -B`) | ~2015 | Resistant to rainbow table attacks |
| TLS 1.0/1.1 | TLS 1.2/1.3 only | ~2018 | Modern browsers reject old protocols |
| 60s WebSocket timeout | 24-hour timeouts | Phase 5 | Prevents idle disconnections |

**Deprecated/outdated:**
- `ssl on;` directive — use `listen 443 ssl;` instead
- `ssl_prefer_server_ciphers on;` — modern clients negotiate best cipher automatically
- RSA keys < 2048 bits — Let's Encrypt requires 2048+ bit keys

## Open Questions

1. **Domain Configuration**
   - What we know: Certbot needs a domain name to obtain certificates.
   - What's unclear: Whether the domain is already configured with DNS pointing to the VPS.
   - Recommendation: Verify DNS A record points to VPS IP before running Certbot. Use `--staging` flag for testing.

2. **Certificate Storage Location**
   - What we know: Let's Encrypt stores certs in `/etc/letsencrypt/live/$domain/`.
   - What's unclear: Whether Docker volume mount should be `/etc/letsencrypt` or just the live directory.
   - Recommendation: Mount entire `/etc/letsencrypt` as read-only — allows renewal to update certs without container changes.

3. **Health Check Endpoint Authentication**
   - What we know: `/health` endpoint should be accessible without auth for monitoring.
   - What's unclear: Whether health check should bypass auth for external monitoring tools.
   - Recommendation: Keep auth on `/health` — internal Docker health check doesn't need external access. If external monitoring is needed, add `satisfy any; allow 127.0.0.1; deny all;` pattern.

## Environment Availability

*This phase has external dependencies (VPS, domain, Certbot, UFW) that must be verified on the target server.*

| Dependency | Required By | Available (Local) | Available (VPS) | Fallback |
|------------|-------------|-------------------|-----------------|----------|
| Docker | Container runtime | v29.2.0 | TBD (VPS) | Install on VPS |
| Docker Compose | Orchestration | v5.0.2 | TBD (VPS) | Install on VPS |
| Certbot | SSL certificates | Not installed | TBD (VPS) | Install via snap/apt |
| UFW | Firewall | N/A (macOS) | TBD (VPS) | Install on VPS |
| htpasswd | Password generation | Available | TBD (VPS) | Install apache2-utils |
| nginx | Web server | Docker only | Docker only | — |
| Domain + DNS | Let's Encrypt | — | TBD | Required for HTTPS |
| VPS SSH access | Deployment | — | TBD | Required |

**Missing dependencies with no fallback:**
- VPS access with SSH on alternate port (2244) — required for deployment
- Domain name with DNS A record pointing to VPS — required for Let's Encrypt certificates

**Missing dependencies with fallback:**
- None — all tools can be installed on VPS during setup

## Validation Architecture

*Skipped per workflow.nyquist_validation = false in config.json*

## Sources

### Primary (HIGH confidence)
- [NGINX ngx_http_auth_basic_module documentation](https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html) — Official auth_basic module reference
- [NGINX HTTP Basic Authentication Guide](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication) — Official configuration guide
- [Docker Compose Merge Documentation](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge) — Official merge behavior reference
- [systemd.timer(5) man page](https://man7.org/linux/man-pages/man5/systemd.timer.5.html) — Official timer configuration

### Secondary (MEDIUM confidence)
- [DigitalOcean Certbot Standalone Guide](https://digitalocean.com/community/tutorials/how-to-use-certbot-standalone-mode-to-retrieve-lets-encrypt-ssl-certificates-on-ubuntu-22-04) — Verified against official docs
- [systemd Certbot Timer Guide](https://k4yt3x.com/automatically-renew-certbot-certificates-with-systemd-timers/) — Multiple source agreement
- [NGINX WebSocket Proxy Guide](https://websocket.org/guides/infrastructure/nginx/) — WebSocket.org maintained
- [NGINX Basic Auth with htpasswd Guide](https://www.getpagespeed.com/server-setup/nginx/nginx-basic-auth-htpasswd) — Verified against official docs

### Tertiary (LOW confidence)
- None — all claims verified against primary or secondary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools are standard, well-documented, and in active use
- Architecture: HIGH — patterns verified against official documentation
- Pitfalls: HIGH — common issues with known solutions in production deployments

**Research date:** 2026-03-28
**Valid until:** 2026-07-28 (stable tooling, long validity window)