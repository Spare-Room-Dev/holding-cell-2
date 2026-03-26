# Phase 5: Docker Containerization - Research

**Researched:** 2026-03-26
**Domain:** Docker Compose multi-service orchestration, Cowrie honeypot containerization, Nginx WebSocket proxy
**Confidence:** HIGH

## Summary

Phase 5 containerizes the existing The Holding Cell application (FastAPI backend, Next.js frontend) and adds Cowrie honeypot, all orchestrated via Docker Compose with proper networking, volume sharing, and health checks. The architecture uses two isolated networks (`app-network` for nginx/frontend/backend, `cowrie-network` for cowrie isolated from app services), nginx as a reverse proxy for WebSocket-aware traffic routing, and shared Docker volumes for log access.

**Primary recommendation:** Use Docker Compose v3.8+ with official Cowrie image (`cowrie/cowrie`), multi-stage Dockerfile for Next.js static export served by nginx, and separate bridge networks for security isolation. Backend reads Cowrie logs via read-only volume mount.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Docker Compose Structure:**
- **D-01:** Four services: nginx (reverse proxy), frontend (Next.js), backend (FastAPI+Socket.io), cowrie (honeypot)
- **D-02:** Nginx handles all external traffic — routes HTTP/WebSocket to backend, serves frontend static files
- **D-03:** Frontend builds to static files, nginx serves them directly (no Next.js server in production)
- **D-04:** Backend runs on port 8000 internally, nginx proxies to it

**Networking & Security:**
- **D-05:** Two separate Docker networks: `app-network` (nginx, frontend, backend) and `cowrie-network` (cowrie, backend via volume only)
- **D-06:** Cowrie isolated — cannot reach backend/frontend/nginx via network, only shares volume for logs
- **D-07:** Backend mounts Cowrie log volume as read-only to read attack data
- **D-08:** No network path from Cowrie to app services (per DEPLOY-04)

**Health Checks:**
- **D-09:** Backend: dedicated `/health` endpoint that returns 200 if FastAPI and Socket.io are running
- **D-10:** Cowrie: process check (`pgrep cowrie`) + port check (`nc -z localhost 2222`)
- **D-11:** Frontend: health check not needed — nginx serves static files, build-time validation
- **D-12:** Nginx: health check not needed — container exits if config invalid
- **D-13:** All services set `restart: unless-stopped` for automatic recovery

**Cowrie Configuration:**
- **D-14:** Cowrie runs with default configuration in Phase 5 — no OT persona yet
- **D-15:** OT persona customization (motd, filesystem, usernames) deferred to Phase 6
- **D-16:** Cowrie JSON logs written to shared volume at `/var/log/cowrie/`
- **D-17:** Cowrie runs as non-root user inside container (per DEPLOY-04)

**Environment & Secrets:**
- **D-18:** Configuration via `.env` file at Docker Compose root — ports, volume paths, service names
- **D-19:** No sensitive secrets in Phase 5 — authentication/SSL come in Phase 8
- **D-20:** `.env.example` checked in, actual `.env` gitignored
- **D-21:** Environment variables passed to containers via `env_file` directive

**Claude's Discretion:**
- Exact Dockerfile structure for each service (follow Docker best practices)
- Exact docker-compose.yml version and syntax (use Compose v3.8+)
- Exact health check intervals and retries (standard values: 30s interval, 3 retries)
- Exact Cowrie image version (use latest stable)

### Deferred Ideas (OUT OF SCOPE)
- OT persona for Cowrie (mining/industrial theme) — Phase 6
- SSL/HTTPS via Let's Encrypt — Phase 8
- Authentication/authorization — Phase 8
- VPS deployment — Phase 8
- Real attack data processing — Phase 6
- Attack persistence — Phase 7
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEPLOY-01 | Docker Compose orchestrates all services (Cowrie, Backend, Frontend, Nginx) | Multi-service docker-compose.yml pattern, service definitions, network configuration |
| DEPLOY-02 | Services restart automatically via Docker health checks | Health check syntax, restart policies, `depends_on` with conditions |
| DEPLOY-03 | Cowrie logs accessible to backend via shared Docker volume | Named volumes, volume mount patterns, read-only mounts |
| DEPLOY-04 | Cowrie runs as non-root user with network isolation from app services | Network segmentation, `internal` networks, container user configuration |
</phase_requirements>

---

## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|---------------|
| Docker | 29.2.0+ | Container runtime | Industry standard, already installed |
| Docker Compose | v5.0.2+ | Multi-container orchestration | Declarative service definition, health checks, networking |
| nginx | alpine | Reverse proxy, static file serving | WebSocket support, minimal image size (~25MB) |
| cowrie/cowrie | latest | SSH/Telnet honeypot | Official image, actively maintained |
| python | 3.11+ | Backend runtime | Matches existing FastAPI backend |
| node | 20-alpine | Frontend build | LTS, minimal image size |

### Supporting

| Library/Tool | Purpose | When to Use |
|--------------|---------|-------------|
| `curl` / `wget` | Health check HTTP requests | Inside containers for HTTP health checks |
| `netcat` / `nc` | Port connectivity checks | Process-level health checks |
| `pgrep` | Process existence checks | Health checks for non-HTTP services |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Official Cowrie image | Build from source | Official is simpler, auto-updates, less maintenance |
| nginx reverse proxy | Caddy, Traefik | nginx is standard, more control over WebSocket config |
| Docker Compose | Kubernetes | Overkill for single-host deployment |
| Static export (output: export) | Next.js standalone server | Static is simpler, no Node runtime needed, nginx serves faster |

**Installation:**
```bash
# Verify Docker and Compose
docker --version
docker compose version

# Build and run all services
docker compose up --build -d
```

---

## Architecture Patterns

### Recommended Project Structure

```
holding-cell/
├── docker-compose.yml          # Main orchestration file
├── .env                        # Environment configuration (gitignored)
├── .env.example               # Template for environment variables
├── backend/
│   ├── Dockerfile             # Python FastAPI container
│   ├── requirements.txt       # Python dependencies
│   └── main.py                # FastAPI app (has /health endpoint)
├── frontend/
│   ├── Dockerfile             # Multi-stage: build → nginx
│   ├── next.config.ts         # Next.js config with output: 'export'
│   └── nginx.conf             # Nginx config for WebSocket proxy
├── cowrie/
│   └── cowrie.cfg             # Custom Cowrie configuration (Phase 6)
└── nginx/
    └── nginx.conf             # Main nginx configuration
```

### Pattern 1: Docker Compose Multi-Service Architecture

**What:** Four-service architecture with two isolated networks

**When to use:** Any multi-service deployment requiring network isolation

**Example:**
```yaml
# Source: Docker Compose best practices, official documentation
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - frontend-static:/usr/share/nginx/html:ro
    networks:
      - app-network
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build: ./frontend
    volumes:
      - frontend-static:/app/out
    networks:
      - app-network
    restart: unless-stopped
    # No health check needed - static build

  backend:
    build: ./backend
    environment:
      - COWRIE_LOG_PATH=/var/log/cowrie
    volumes:
      - cowrie-logs:/var/log/cowrie:ro
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped

  cowrie:
    image: cowrie/cowrie:latest
    ports:
      - "2222:2222"  # SSH
      - "2323:2223"  # Telnet (optional)
    volumes:
      - cowrie-logs:/cowrie/cowrie-git/var/log/cowrie
    networks:
      - cowrie-network
    healthcheck:
      test: ["CMD-SHELL", "pgrep cowrie && nc -z localhost 2222"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
    # Runs as non-root by default in official image

networks:
  app-network:
    driver: bridge
  cowrie-network:
    driver: bridge
    internal: true  # No external internet access from Cowrie

volumes:
  frontend-static:
  cowrie-logs:
```

### Pattern 2: Network Isolation for Security

**What:** Separate networks prevent Cowrie from reaching app services

**When to use:** Any honeypot or untrusted service deployment

**Example:**
```yaml
# Cowrie has NO access to app-network
# Backend has NO access to cowrie-network
# They communicate only through shared volume

services:
  cowrie:
    networks:
      - cowrie-network  # Isolated network
    # No app-network membership

  backend:
    networks:
      - app-network     # App network only
    volumes:
      - cowrie-logs:/var/log/cowrie:ro  # Read-only volume access

networks:
  cowrie-network:
    internal: true  # Blocks external internet access
```

**Security principle:** Cowrie can only write logs to shared volume. Backend can only read logs. No network path between them.

### Pattern 3: Nginx WebSocket Proxy Configuration

**What:** Nginx configuration for Socket.io WebSocket connections

**When to use:** Any real-time application with Socket.io behind nginx

**Example:**
```nginx
# Source: Socket.io official docs, nginx WebSocket proxy guide
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name localhost;

    # Frontend static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # WebSocket/Socket.io endpoint
    location /socket.io/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;

        # Required for WebSocket upgrade
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Extended timeouts for WebSocket
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Pattern 4: Multi-Stage Dockerfile for Frontend

**What:** Build Next.js as static files, serve with nginx

**When to use:** Production Next.js deployment without Node.js runtime

**Example:**
```dockerfile
# Source: Next.js Docker best practices, official Docker blog
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM nginx:alpine AS production
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```javascript
// next.config.ts
const nextConfig = {
  output: 'export',  // Static export
  // Required for static export
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};
```

### Pattern 5: Health Check Implementation

**What:** Container health checks for automatic restart

**When to use:** All production Docker deployments

**Example - Backend (HTTP endpoint):**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

**Example - Cowrie (Process + Port):**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pgrep cowrie && nc -z localhost 2222"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s  # Cowrie takes longer to start
```

### Anti-Patterns to Avoid

- **Using `localhost` in Docker Compose:** Use service names (e.g., `backend:8000` not `localhost:8000`)
- **Default bridge network for all services:** Creates security risks, no network isolation
- **Health checks without `start_period`:** Slow-starting containers get marked unhealthy prematurely
- **Volume mounts with `:rw` for logs that only need reading:** Use `:ro` for security
- **Missing WebSocket headers in nginx:** Causes 60-second disconnects or 400 errors

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cowrie honeypot | Custom SSH honeypot | `cowrie/cowrie` image | Battle-tested, actively maintained, logs in JSON format |
| WebSocket proxy | Custom nginx config from scratch | Standard Socket.io nginx config | Known working pattern, handles upgrade headers |
| Health check script | Complex multi-line script | Simple `curl -f` or `pgrep` | Built into Docker, simpler maintenance |
| Log sharing | Custom API between containers | Docker named volumes | Simpler, filesystem-based, no network exposure |
| Process monitoring | Custom watchdog script | Docker health checks + `restart: unless-stopped` | Built-in orchestration, automatic recovery |

**Key insight:** Docker Compose provides orchestration primitives (health checks, restart policies, networks, volumes) that replace custom scripts. Use them.

---

## Common Pitfalls

### Pitfall 1: WebSocket Connection Drops After 60 Seconds

**What goes wrong:** Nginx default timeout terminates WebSocket connections.

**Why it happens:** Default `proxy_read_timeout` is 60s; long-lived WebSocket connections get cut.

**How to avoid:** Set extended timeouts in nginx config:
```nginx
proxy_read_timeout 86400s;  # 24 hours
proxy_send_timeout 86400s;
```

**Warning signs:** Socket.io clients reconnect repeatedly, "SIGNAL LOST" banner flickers.

### Pitfall 2: Cowrie Can Reach Backend Over Network

**What goes wrong:** Cowrie container can make network requests to backend, creating security risk.

**Why it happens:** All containers on default bridge network can communicate.

**How to avoid:** Use separate networks:
- `app-network`: nginx, frontend, backend
- `cowrie-network`: cowrie only (with `internal: true`)

**Warning signs:** `docker network inspect` shows Cowrie connected to same network as backend.

### Pitfall 3: Health Check Fails During Slow Startup

**What goes wrong:** Container marked unhealthy and restarted before it finishes initializing.

**Why it happens:** Default `start_period` is 0s; slow-starting services get marked unhealthy.

**How to avoid:** Set appropriate `start_period`:
- Python/FastAPI: 30s
- Cowrie: 60s (loads more dependencies)
- Node.js: 20-30s

**Warning signs:** Containers enter restart loop, `docker ps` shows "unhealthy" status.

### Pitfall 4: Volume Mounts Wipe Container Files

**What goes wrong:** Mounting a volume to `/cowrie/cowrie-git/etc` removes existing config files.

**Why it happens:** Docker volume mount overlays container directory.

**How to avoid:** Mount specific files or use environment variables:
```yaml
# Preferred: environment variables
environment:
  - COWRIE_TELNET_ENABLED=yes

# If mounting volumes, copy existing files first
volumes:
  - ./cowrie/etc:/cowrie/cowrie-git/etc:ro
```

**Warning signs:** Cowrie fails to start, "missing config file" errors.

### Pitfall 5: Frontend Cannot Connect to Backend WebSocket

**What goes wrong:** Browser clients get 400/502 errors when connecting to Socket.io.

**Why it happens:** Missing `Upgrade` and `Connection` headers in nginx config.

**How to avoid:** Include all three required headers:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

**Warning signs:** Browser console shows "400 Bad Request" on Socket.io connection.

### Pitfall 6: Static Export Breaks Client-Side Routing

**What goes wrong:** Next.js static export doesn't handle client-side navigation properly.

**Why it happens:** Static export requires `trailingSlash: true` and `images.unoptimized: true`.

**How to avoid:** Configure Next.js for static export:
```javascript
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
};
```

---

## Code Examples

### Backend Dockerfile

```dockerfile
# Source: Python Docker best practices
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check endpoint already exists in main.py
EXPOSE 8000

CMD ["uvicorn", "main:combined_app", "--host", "0.0.0.0", "--port", "8000"]
```

### Backend Health Endpoint (Already Exists)

```python
# backend/main.py - Already implemented
@app.get('/health')
async def health_check() -> dict:
    """Health check endpoint for Docker health checks."""
    return {"status": "ok"}
```

### Frontend Dockerfile (Multi-Stage)

```dockerfile
# Source: Next.js Docker official guide
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production (nginx serves static files)
FROM nginx:alpine AS production
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment File Template

```bash
# .env.example - Checked into git
BACKEND_PORT=8000
FRONTEND_PORT=3000
COWRIE_SSH_PORT=2222
COWRIE_TELNET_PORT=2323

# Service names (Docker Compose internal)
BACKEND_HOST=backend
FRONTEND_HOST=frontend
NGINX_HOST=nginx
COWRIE_HOST=cowrie

# Volume paths
COWRIE_LOG_PATH=/var/log/cowrie
```

### docker-compose.yml (Complete)

```yaml
# Source: Docker Compose best practices
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "${FRONTEND_PORT:-80}:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - frontend-static:/usr/share/nginx/html:ro
    networks:
      - app-network
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - frontend-static:/app/out
    networks:
      - app-network
    restart: unless-stopped
    # No health check - static files served by nginx

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - COWRIE_LOG_PATH=${COWRIE_LOG_PATH:-/var/log/cowrie}
    volumes:
      - cowrie-logs:${COWRIE_LOG_PATH:-/var/log/cowrie}:ro
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped

  cowrie:
    image: cowrie/cowrie:latest
    ports:
      - "${COWRIE_SSH_PORT:-2222}:2222"
      - "${COWRIE_TELNET_PORT:-2323}:2223"
    volumes:
      - cowrie-logs:/cowrie/cowrie-git/var/log/cowrie
    networks:
      - cowrie-network
    healthcheck:
      test: ["CMD-SHELL", "pgrep cowrie && nc -z localhost 2222"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
    # Official image runs as non-root 'cowrie' user by default

networks:
  app-network:
    driver: bridge
  cowrie-network:
    driver: bridge
    internal: true

volumes:
  frontend-static:
  cowrie-logs:
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|-------|
| `docker-compose` (v1) | `docker compose` (v2) | Docker 20.10+ | Integrated into Docker CLI |
| `links` for dependencies | `depends_on` with conditions | Compose v2.1+ | Declarative dependency ordering |
| Single bridge network | Multiple isolated networks | Security best practice | Network segmentation |
| `restart: always` | `restart: unless-stopped` | Compose v3+ | Better controlled restarts |
| Volume mounts for logs | Named volumes | Docker best practice | Better volume management |

**Deprecated/outdated:**
- `docker-compose.yml` version `2` or `2.x`: Use `3.8` for latest features
- `links` directive: Use `depends_on` with health conditions
- `expose` without `ports`: Use internal networks instead

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Docker | All services | ✓ | 29.2.0 | — |
| Docker Compose | Orchestration | ✓ | v5.0.2 | — |
| Node.js 20 | Frontend build | ✓ | — | Multi-stage build uses node:20-alpine |
| Python 3.11+ | Backend runtime | ✓ | — | Backend Dockerfile uses python:3.11-slim |
| nginx | Reverse proxy | ✓ | alpine | — |
| Cowrie image | Honeypot | ✓ | latest | — |

**Missing dependencies with no fallback:** None — all required tools are available.

**Missing dependencies with fallback:** None — all required tools are available.

---

## Open Questions

1. **Cowrie Log Rotation**
   - What we know: Cowrie writes JSON logs continuously
   - What's unclear: Whether log rotation is needed in Phase 5 or can be deferred
   - Recommendation: Defer to Phase 7 (persistence). Phase 5 focuses on containerization, not log management.

2. **Telnet Port Exposure**
   - What we know: Cowrie supports Telnet on port 2223, can be mapped to 2323 externally
   - What's unclear: Whether to enable Telnet in Phase 5
   - Recommendation: Include in docker-compose but disabled by default (`COWRIE_TELNET_ENABLED=no`). Enable in Phase 6 if needed for OT persona.

3. **Backend Volume Mount Path**
   - What we know: Cowrie logs are at `/cowrie/cowrie-git/var/log/cowrie/cowrie.json` inside container
   - What's unclear: Exact mount point for backend to read
   - Recommendation: Mount volume at `/var/log/cowrie` in backend, set `COWRIE_LOG_PATH` env var.

---

## Sources

### Primary (HIGH confidence)
- [Docker Compose Networking Documentation](https://docs.docker.com/reference/compose-file/networks) - Network configuration syntax
- [Docker Health Checks Guide](https://docs.docker.com/compose/how-tos/startup-order) - Health check best practices
- [Cowrie Docker Documentation](https://docs.cowrie.org/en/stable/docker/README.html) - Official Cowrie Docker configuration

### Secondary (MEDIUM confidence)
- [Docker Hub - Cowrie Image](https://hub.docker.com/r/cowrie/cowrie) - Image details and environment variables
- [Nginx WebSocket Proxy Guide](https://oneuptime.com/blog/post/2026-01-25-nginx-websocket-proxy/) - WebSocket configuration
- [Socket.io Nginx Configuration](https://oneuptime.com/blog/post/2025-12-16-socketio-nginx-configuration/) - Socket.io specific settings
- [Next.js Docker with Compose](https://docker.com/blog/how-to-build-and-run-next-js-applications-with-docker-compose-nginx) - Static export pattern
- [Docker Compose Health Checks](https://last9.io/blog/docker-compose-health-checks) - Health check patterns

### Tertiary (LOW confidence)
- [Cowrie GitHub Issues](https://github.com/cowrie/cowrie/issues/2449) - Configuration troubleshooting

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Docker/Compose/nginx/Cowrie all well-documented with official images
- Architecture: HIGH - Standard multi-service patterns, network isolation well-established
- Pitfalls: HIGH - Common WebSocket and health check issues documented extensively

**Research date:** 2026-03-26
**Valid until:** 90 days (stable Docker/Compose patterns, but check Cowrie image for updates)