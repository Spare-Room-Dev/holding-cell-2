# Stack Research: The Holding Cell

**Domain:** Real-time SOC dashboard + Honeypot integration + Docker deployment
**Researched:** 2026-03-26
**Confidence:** HIGH (verified via PyPI, Docker Hub, official docs)

---

## Recommended Stack

### Core Technologies (EXISTING - Validated)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Next.js** | 14.x (App Router) | React framework, frontend | App Router is the 2024-2025 standard. Server components reduce client bundle. Stable Socket.io client integration. |
| **React** | 18.x | UI library | Comes with Next.js 14. Concurrent features available if needed. |
| **TypeScript** | 5.x | Type safety | Catches AttackEvent shape mismatches at compile time. |
| **Tailwind CSS** | 3.4.x | Utility CSS | Rapid iteration on retro-futuristic aesthetic. DESIGN.md tokens map directly. |
| **Framer Motion** | 11.x | Animation | Prisoner entrance animation requires spring physics. CSS keyframes cannot replicate organic bounce. |
| **Socket.io Client** | 4.x | Real-time WebSocket | Mature auto-reconnect, fallback transport, typed events. |

### Backend Technologies (EXISTING - Validated)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.11+ | Language runtime | PLAN.md specifies 3.11+. 3.12 offers ~10% faster interpreter. |
| **FastAPI** | 0.135.x (verified Mar 2026) | ASGI web framework | Native async, Pydantic v2 integration, OpenAPI auto-docs. Cowrie integration is Python-native. |
| **python-socketio** | 5.16.x (verified Mar 2026) | Async WebSocket server | Full async support with ASGI mode. Cross-worker communication via Redis. |
| **uvicorn** | 0.34.x | ASGI server | Standard for FastAPI. Use `--ws websockets` for Socket.IO. |
| **Pydantic** | 2.x | Data validation | AttackEvent model validation. v2 has significant performance gains. |

### NEW: Cowrie Integration Stack

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Cowrie** | `cowrie/cowrie:latest` (v2.9.x) | SSH/Telnet honeypot | Industry-standard medium-interaction honeypot. Docker-first deployment. JSON output for easy parsing. |
| **watchdog** | `>=3.0.0` | File system watcher | Poll cowrie.json for new attack events. Non-blocking async integration. |
| **aiofiles** | `>=23.0.0` | Async file operations | Read Cowrie logs without blocking FastAPI event loop. |

### NEW: Docker Deployment Stack

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Docker Compose** | v3.8 syntax | Multi-container orchestration | De facto standard for single-VPS deployment. Handles backend, frontend, Cowrie, Redis with single command. |
| **Nginx** | `nginx:1.27-alpine` | Reverse proxy + SSL termination | Required for WebSocket support (Socket.IO), HTTPS via Let's Encrypt, production-grade routing. |
| **Certbot** | `certbot/certbot:latest` | SSL certificate automation | Official Let's Encrypt client. Auto-renewal for 90-day certificates. |
| **Redis** | `redis:7-alpine` | Socket.IO message broker | Enables multi-worker Socket.IO events. Also useful for caching. |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          VPS (Public IP)                             │
│                                                                      │
│  ┌──────────────┐     ┌───────────────────────────────────────────┐ │
│  │   Nginx      │     │         Docker Network                    │ │
│  │  :443 HTTPS  │────▶│  ┌─────────┐ ┌─────────┐ ┌─────────┐     │ │
│  │  :80 HTTP    │     │  │ Backend │ │Frontend │ │ Cowrie  │     │ │
│  └──────────────┘     │  │ :8000   │ │ :3000   │ │ :2222   │     │ │
│         │              │  └────┬────┘ └─────────┘ └────┬────┘     │ │
│         ▼              │       │                       │          │ │
│  ┌──────────────┐     │       ▼                       │          │ │
│  │   Certbot    │     │  ┌─────────┐                  │          │ │
│  │ Let's Encrypt│     │  │  Redis  │◀──Event bus────┘          │ │
│  └──────────────┘     │  │ :6379   │  (future scaling)          │ │
│                       │  └─────────┘                             │ │
│                       └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow (Cowrie Integration)

```
Attacker ──SSH/Telnet──▶ Cowrie :2222
                              │
                              ▼ (writes JSON log)
                         cowrie.json
                              │
                              ▼ (watchdog polling)
                    Backend FastAPI :8000
                              │
                              ▼ (Socket.IO emit)
                    Frontend Next.js :3000
```

---

## Docker Compose Configuration

```yaml
# docker-compose.yml

version: "3.8"

services:
  # ============================================
  # COWRIE HONEYPOT - SSH/Telnet attack capture
  # ============================================
  cowrie:
    image: cowrie/cowrie:latest
    restart: unless-stopped
    ports:
      - "22:2222"      # SSH (map to real port 22 for realism)
      - "23:2223"      # Telnet (optional)
    volumes:
      - cowrie-var:/cowrie/cowrie-git/var
      - ./cowrie/etc:/cowrie/cowrie-git/etc:ro
    networks:
      - holding-cell-net
    environment:
      - COWRIE_SSH_ENABLED=true
      - COWRIE_TELNET_ENABLED=true

  # ============================================
  # REDIS - Socket.IO message broker
  # ============================================
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - holding-cell-net
    command: redis-server --appendonly yes

  # ============================================
  # BACKEND - FastAPI + python-socketio
  # ============================================
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      - redis
      - cowrie
    environment:
      - REDIS_URL=redis://redis:6379/0
      - COWRIE_LOG_PATH=/var/log/cowrie/cowrie.json
      - CORS_ORIGINS=https://yourdomain.com
    volumes:
      - cowrie-var:/var/log/cowrie:ro  # Read-only access to Cowrie logs
    networks:
      - holding-cell-net
    expose:
      - "8000"

  # ============================================
  # FRONTEND - Next.js 14 App Router
  # ============================================
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_BACKEND_URL=https://yourdomain.com
      - NEXT_PUBLIC_SOCKET_PATH=/socket.io
    networks:
      - holding-cell-net
    expose:
      - "3000"

  # ============================================
  # NGINX - Reverse proxy + SSL termination
  # ============================================
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - backend
      - frontend
    networks:
      - holding-cell-net
    command: "/bin/sh -c 'while :; do sleep 6h & wait $${!}; nginx -s reload; done & nginx -g \"daemon off;\"'"

  # ============================================
  # CERTBOT - Let's Encrypt SSL automation
  # ============================================
  certbot:
    image: certbot/certbot:latest
    restart: unless-stopped
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  cowrie-var:
  redis-data:

networks:
  holding-cell-net:
    driver: bridge
```

---

## Nginx Configuration (WebSocket Support)

```nginx
# nginx.conf - Critical for Socket.IO WebSocket support

upstream backend_upstream {
    server backend:8000;
    keepalive 32;
}

upstream frontend_upstream {
    server frontend:3000;
    keepalive 32;
}

# Map for WebSocket upgrade (REQUIRED for Socket.IO)
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # TLS best practices (2025)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;

    # Frontend (Next.js)
    location / {
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://frontend_upstream;
    }

    # Backend API
    location /api/ {
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://backend_upstream;
    }

    # Socket.IO WebSocket (CRITICAL - requires special headers)
    location /socket.io/ {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://backend_upstream;
        proxy_read_timeout 86400s;  # 24h for long-lived WebSocket
    }
}
```

---

## Backend Dockerfile

```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run with Uvicorn (single worker for development)
# For production multi-worker: use Gunicorn with UvicornWorker
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Frontend Dockerfile (Next.js Standalone)

```dockerfile
# frontend/Dockerfile

# Stage 1: Dependencies
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy standalone output (requires next.config.js: output: 'standalone')
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**Note:** Add `output: 'standalone'` to `next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};

module.exports = nextConfig;
```

---

## Requirements Additions (backend/requirements.txt)

```txt
# Existing (from PROJECT.md)
fastapi>=0.100.0
python-socketio[asyncio]>=5.10.0
uvicorn[standard]>=0.23.0
httpx>=0.24.0
pydantic>=2.0.0

# NEW for Cowrie integration + Docker deployment
redis>=5.0.0           # AsyncRedisManager for Socket.IO scaling
watchdog>=3.0.0        # File system watcher for cowrie.json
aiofiles>=23.0.0       # Async file operations
```

---

## Cowrie Integration Approach

### Event Types (from cowrie.json log)

| Event ID | When It Fires | Key Fields |
|----------|---------------|------------|
| `cowrie.session.connect` | New SSH/Telnet connection | `src_ip`, `src_port`, `dst_ip`, `dst_port` |
| `cowrie.login.failed` | Failed authentication attempt | `username`, `password` |
| `cowrie.login.success` | Successful authentication | `username`, `password` |
| `cowrie.command.input` | Attacker executes command | `input` (the command) |
| `cowrie.session.closed` | Connection ends | `duration`, `session` |

### Backend Log Watcher Pattern

```python
# backend/cowrie_watcher.py
import asyncio
import json
import aiofiles
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CowrieLogHandler(FileSystemEventHandler):
    """Watch cowrie.json for new attack events."""

    def __init__(self, socket_server, log_path: str):
        self.socket_server = socket_server
        self.log_path = log_path
        self.position = 0

    async def process_new_events(self):
        """Read new lines from cowrie.json since last position."""
        async with aiofiles.open(self.log_path, 'r') as f:
            await f.seek(self.position)
            async for line in f:
                event = json.loads(line.strip())
                await self.handle_event(event)
            self.position = await f.tell()

    async def handle_event(self, event: dict):
        """Convert Cowrie event to Socket.IO emission."""
        event_id = event.get('eventid')

        if event_id == 'cowrie.session.connect':
            # New attacker - create prisoner
            await self.socket_server.emit('new_attack', {
                'session': event['session'],
                'src_ip': event['src_ip'],
                'timestamp': event['timestamp'],
            })
        elif event_id == 'cowrie.login.success':
            # Successful brute force - mark as "suspicious"
            await self.socket_server.emit('attack_update', {
                'session': event['session'],
                'type': 'credential_success',
                'username': event['username'],
            })
        # ... handle other events
```

---

## Installation

### Frontend (Next.js) - No changes

```bash
cd frontend
npm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
npm install socket.io-client@4 framer-motion@11 clsx tailwind-merge
```

### Backend (Python) - Updated with new deps

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Core (existing)
pip install fastapi uvicorn[standard] "python-socketio[asyncio]" httpx pydantic

# NEW for Cowrie + Docker
pip install redis watchdog aiofiles
```

### Docker Deployment

```bash
# Initial SSL certificate (run once)
docker compose run --rm certbot certonly --webroot \
  --webroot-path /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com

# Start all services
docker compose up -d

# Verify HTTPS
curl -I https://yourdomain.com

# Test Cowrie (should hit honeypot)
ssh root@yourdomain.com
```

---

## Alternatives Considered

| Category | Recommended | Alternative | When to Use Alternative |
|----------|-------------|-------------|-------------------------|
| Real-time transport | Socket.io (client 4.x) | SSE (Server-Sent Events) | SSE simpler for one-way server→client only. Socket.io preferred for future client→server commands. |
| Animation library | Framer Motion 11.x | CSS keyframes / React Spring | CSS keyframes cannot do spring physics bounce. React Spring lighter but Framer Motion API more ergonomic. |
| Backend framework | FastAPI | Flask + Socket.io | Flask sync-only. FastAPI async pairs better with python-socketio. |
| WebSocket server | python-socketio 5.x | websockets (bare library) | websockets lower-level. python-socketio adds rooms, auto-reconnect, fallback. |
| **Docker orchestration** | **Docker Compose** | Kubernetes | Scale beyond single VPS, need auto-scaling |
| **Docker orchestration** | **Docker Compose** | Ansible + systemd | Bare-metal servers without Docker |
| **Reverse proxy** | **Nginx** | Caddy | Simpler setup, automatic HTTPS (no Certbot) |
| **Reverse proxy** | **Nginx** | Traefik | Native Docker integration, auto-discovery |
| **Socket.IO scaling** | **Redis** | Kafka | Enterprise scale, need message persistence |
| **Cowrie log parsing** | **watchdog polling** | Cowrie output plugin | Direct database writes (requires Cowrie config changes) |
| **Cowrie deployment** | **Docker image** | Bare-metal install | Need custom patches or hardware access |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Socket.io 3.x** | Async support second-class. Forces thread-based event loop. | python-socketio 5.x with asyncio engine |
| **Next.js 13 (Pages Router)** | App Router is current standard. Pages Router in maintenance mode. | Next.js 14 App Router |
| **Pydantic v1** | End of life. FastAPI 0.110+ requires v2. | Pydantic v2 |
| **Flask** | Sync-only. Cowrie integration is Python-native. | FastAPI |
| **Raw WebSocket API** | No auto-reconnect, no fallback, no room semantics. | Socket.io client 4.x |
| **Running Cowrie as root** | Security disaster - exposes system to attacks. | Dedicated `cowrie` user (Docker handles this) |
| **Long-polling transport** | Requires sticky sessions, more complex load balancing. | WebSocket-only (`transports=['websocket']`) |
| **HTTP on public internet** | MITM attacks, credential theft. | HTTPS only via Let's Encrypt |
| **SQLite for Cowrie output** | Not designed for real-time queries. | JSON logs + file watcher (simplest) or PostgreSQL (scale) |
| **Uvicorn multi-worker without Redis** | Socket.IO events won't reach all clients. | Single worker OR Redis message broker |

---

## Stack Patterns by Variant

**If scaling beyond single VPS:**
- Add Kubernetes or Docker Swarm
- Redis becomes mandatory for cross-instance Socket.IO
- Consider managed Redis (Upstash, Redis Cloud)

**If adding Shodan enrichment (Weekend 3):**
- Add `GET /shodan/{ip}` endpoint to FastAPI
- Add `httpx` async calls with rate limiting (Shodan has 1 req/sec free tier)
- Consider caching responses in Redis

**If aggregating multiple honeypots (v2+):**
- Redis pub/sub becomes mandatory for event distribution
- FastAPI workers consume from queue and emit to Socket.io
- Consider message queue (Kafka, RabbitMQ) for persistence

---

## Version Compatibility Matrix

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| python-socketio | 5.16.x | Python 3.8-3.13 | AsyncRedisManager requires `redis` package |
| FastAPI | 0.135.x | python-socketio 5.x | Use `ASGIApp` wrapper for Socket.IO |
| uvicorn | 0.34.x | FastAPI, python-socketio | Use `--ws websockets` for WebSocket support |
| Next.js | 14.x | Node 18+ | Project on 14, upgrade to 15 optional |
| Redis | 7.x | python-socketio | AsyncRedisManager compatible |
| Cowrie | v2.9.x | Docker | Official image on Docker Hub |

---

## Sources

**HIGH confidence (verified via official sources):**

- [PyPI] python-socketio 5.16.1 — https://pypi.org/project/python-socketio/ (verified Mar 2026)
- [PyPI] FastAPI 0.135.2 — https://pypi.org/project/fastapi/ (verified Mar 2026)
- [Docker Hub] cowrie/cowrie — https://hub.docker.com/r/cowrie/cowrie (verified Mar 2026)
- [Official Docs] Cowrie Output Events — https://docs.cowrie.org/en/latest/OUTPUT.html
- [Official Docs] Cowrie LLM Backend — https://docs.cowrie.org/en/latest/LLM.html
- [Socket.IO Docs] Redis Adapter — https://socket.io/docs/v4/redis-adapter
- [GitHub] cowrie/cowrie — v2.9.14, 6,241 stars
- [Better Stack] FastAPI Docker Best Practices — Production deployment guide
- [Medium] FastAPI + Socket.IO Integration — ASGIApp wrapper pattern
- [OneUptime] Cowrie Setup Guide — https://oneuptime.com/blog/post/2026-03-02-how-to-set-up-a-honeypot-with-cowrie-on-ubuntu/view
- [PhoenixNAP] Let's Encrypt Nginx Guide — https://phoenixnap.com/kb/letsencrypt-nginx
- [Dev.to] Socket.IO Redis Scaling — https://dev.to/codexam/scaling-real-time-communication-with-redis-pubsub-and-socketio-3p56

---

## Verification Checklist

Before deployment, verify:

```bash
# Frontend versions
npm view next version
npm view framer-motion version
npm view socket.io-client version
npm view tailwindcss version

# Backend versions
pip show fastapi | grep Version
pip show python-socketio | grep Version
pip show uvicorn | grep Version
pip show redis | grep Version
pip show watchdog | grep Version

# Docker images
docker pull cowrie/cowrie:latest
docker pull nginx:1.27-alpine
docker pull redis:7-alpine
docker pull certbot/certbot:latest
```

---

*Stack research for: The Holding Cell - Cowrie Integration, Docker Deployment, VPS Hosting*
*Researched: 2026-03-26*
*Previous research: 2026-03-24 (existing stack, now extended)*