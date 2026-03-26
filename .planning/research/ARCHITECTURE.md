# Architecture Research

**Domain:** SOC / Threat Intelligence Visualization Dashboard + Cowrie Honeypot Integration
**Researched:** 2026-03-26 (Updated for Milestone v1.1)
**Confidence:** HIGH

## Standard Architecture

### System Overview (v1.0 - Development)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐   ┌───────────────────┐   ┌────────────────────────┐ │
│  │  JailCellGrid   │   │    StatsPanel     │   │   Header/LiveBadge     │ │
│  │  (visualization)│   │  (counters/kpis)  │   │  (connection status)   │ │
│  └────────┬─────────┘   └─────────┬────────┘   └───────────┬────────────┘ │
│           │                       │                         │              │
│           └───────────────────────┼─────────────────────────┘              │
│                                   │ WebSocket (Socket.io client)           │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │ ws://host:port
                                    │
┌───────────────────────────────────┼─────────────────────────────────────────┐
│                    BACKEND (FastAPI + Socket.io)                            │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  ┌────────────────────────────────┴─────────────────────────────────────┐  │
│  │                    SocketServer (event broadcaster)                   │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐   │
│  │              AttackSource (honeypot / fake generator)                │   │
│  │  - Cowrie honeypot log tailer (Weekend 2)                           │   │
│  │  - Fake attack generator (Weekend 1, Approach A)                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### System Overview (v1.1 - Production with Cowrie + Docker)

```
                                    PRODUCTION DEPLOYMENT
                                    ────────────────────────────────────────
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                              VPS (Production)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │
│  │    Nginx        │    │   Cowrie        │    │   Docker Bridge Network │ │
│  │  (Reverse Proxy)│    │   (Honeypot)    │    │   (internal comms)      │ │
│  │  :80, :443      │    │   :22→2222      │    │                         │ │
│  │  TLS Termination│    │   :23→2223      │    │                         │ │
│  └────────┬────────┘    └────────┬────────┘    └─────────────────────────┘ │
│           │                      │                                         │
│           │                      │ cowrie.json                             │
│           │                      ▼                                         │
│  ┌────────▼────────┐    ┌────────────────┐    ┌─────────────────────┐    │
│  │   Frontend       │    │    Backend      │    │  Docker Volume      │    │
│  │   (Next.js)      │◄───│   (FastAPI +    │◄───│  cowrie-logs        │    │
│  │   :3000          │    │   python-socketio)│    │  (shared)           │    │
│  │                  │    │   :8000          │    │                     │    │
│  └─────────────────┘    │                  │    └─────────────────────┘    │
│                         │  ┌───────────────┤                              │
│                         │  │ CowrieLog     │                              │
│                         │  │ Monitor       │ (file watcher)              │
│                         │  └───────────────┘                              │
│                         └──────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **AttackSource** | Generate or forward raw attack events | FakeGenerator (Weekend 1) or CowrieLogMonitor (Weekend 2) |
| **SocketServer** | Broadcast events to all connected clients | python-socketio async server (existing) |
| **JailCellGrid** | Visualize attacker "prisoners" in jail cell | React + Framer Motion (existing) |
| **StatsPanel** | Aggregate counters (archetype tallies, totals) | React + useReducer (existing) |
| **Header/LiveBadge** | Connection status and system health | React component (existing) |
| **ArchetypeClassifier** | Classify honeypot logs into attacker archetypes | Rule-based classifier (existing) |
| **Nginx** (NEW) | TLS termination, reverse proxy, WebSocket upgrade | Official nginx Docker image |
| **CowrieLogMonitor** (NEW) | Watch cowrie.json, parse events, emit via Socket.io | Python watchdog + asyncio bridge |
| **Cowrie** (NEW) | SSH/Telnet honeypot, capture attack sessions | Official cowrie/cowrie Docker image |

## Recommended Project Structure (Updated for v1.1)

```
holding-cell-2/
├── docker-compose.yml          # Production orchestration (NEW)
├── docker-compose.dev.yml      # Development (fake data only) (NEW)
├── backend/
│   ├── main.py                 # FastAPI + Socket.io (existing)
│   ├── attack_generator.py     # Fake attack generator (existing)
│   ├── cowrie_monitor.py       # NEW: File watcher for cowrie.json
│   ├── archetypes.py           # Archetype classification (existing)
│   ├── models.py               # Pydantic models (existing)
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # NEW: Backend container
├── frontend/
│   ├── src/                    # Next.js app (existing)
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile              # NEW: Frontend container
├── cowrie/
│   ├── cowrie.cfg              # Cowrie configuration (NEW)
│   └── userdb.txt              # User database for honeypot (NEW)
├── nginx/
│   ├── nginx.conf              # Reverse proxy configuration (NEW)
│   └── ssl/                    # Certbot certificates (mounted) (NEW)
├── DESIGN.md
├── PLAN.md
├── CLAUDE.md
└── .planning/
    ├── PROJECT.md
    └── research/
        ├── ARCHITECTURE.md
        ├── FEATURES.md
        ├── PITFALLS.md
        ├── STACK.md
        └── SUMMARY.md
```

### Structure Rationale

- **backend/cowrie_monitor.py:** New module for file watching - separates concerns from fake generator. Environment variable `DATA_SOURCE` selects between fake and real.
- **cowrie/:** Isolated Cowrie configuration - easier to manage honeypot settings without touching app code.
- **nginx/:** Production reverse proxy configuration separate from app code. Handles TLS termination.
- **docker-compose.yml:** Production config with Cowrie, Nginx, Backend, Frontend.
- **docker-compose.dev.yml:** Development without Cowrie (fake data only) - simpler iteration cycle.

## Architectural Patterns

### Pattern 1: Dual Data Source (Fake + Real)

**What:** Backend supports both fake attack generation (development) and real Cowrie data (production) via environment variable.

**When to use:** Development iteration requires fake data; production needs real honeypot data.

**Trade-offs:**
- Pro: Fast development cycle without running Cowrie locally
- Pro: Same codebase works in both environments
- Con: Slight code complexity in startup logic

**Example:**
```python
# main.py - Environment-based data source selection
import os

DATA_SOURCE = os.getenv("DATA_SOURCE", "fake")  # "fake" or "cowrie"

@app.on_event('startup')
async def startup() -> None:
    if DATA_SOURCE == "cowrie":
        asyncio.create_task(cowrie_log_monitor())
    else:
        asyncio.create_task(attack_emitter())
```

### Pattern 2: File Watching with asyncio Bridge

**What:** Watchdog (synchronous) monitors cowrie.json, uses asyncio bridge to emit Socket.io events.

**When to use:** Cowrie writes to file; need real-time emission without blocking the event loop.

**Trade-offs:**
- Pro: No network hop between Cowrie and Backend (shared volume)
- Pro: Cowrie writes independently; Backend picks up events
- Con: Requires careful event loop handling (watchdog is sync, Socket.io is async)

**Example:**
```python
# cowrie_monitor.py
import asyncio
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CowrieLogHandler(FileSystemEventHandler):
    def __init__(self, sio, loop, last_position=0):
        self.sio = sio
        self.loop = loop
        self.last_position = last_position

    def on_modified(self, event):
        if event.src_path.endswith('cowrie.json'):
            new_events = self._read_new_events(event.src_path)
            for event_data in new_events:
                # Bridge sync watchdog to async Socket.io
                asyncio.run_coroutine_threadsafe(
                    self.sio.emit('attack_event', event_data),
                    self.loop
                )

    def _read_new_events(self, path):
        """Read only new lines since last position (tail -f pattern)."""
        with open(path, 'r') as f:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()
        return [self._parse_event(line) for line in new_lines if line.strip()]

async def cowrie_log_monitor():
    """Background task that monitors Cowrie JSON logs."""
    loop = asyncio.get_running_loop()
    observer = Observer()
    handler = CowrieLogHandler(sio, loop)
    observer.schedule(handler, path="/app/cowrie-logs", recursive=False)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        observer.stop()
        observer.join()
```

### Pattern 3: Docker Volume Sharing for Log Files

**What:** Cowrie container writes to a Docker volume; backend container reads from the same volume.

**When to use:** Inter-container file sharing without network overhead.

**Trade-offs:**
- Pro: No network hop, simple architecture
- Pro: Both containers can run independently
- Con: Requires both containers on same host (tight coupling)
- Con: Must handle file rotation and position tracking

**Example (docker-compose.yml):**
```yaml
volumes:
  cowrie-logs:

services:
  cowrie:
    image: cowrie/cowrie:latest
    volumes:
      - cowrie-logs:/cowrie/cowrie-git/var/log/cowrie
    ports:
      - "22:2222"   # SSH on port 22
      - "23:2223"   # Telnet on port 23 (optional)

  backend:
    build: ./backend
    volumes:
      - cowrie-logs:/app/cowrie-logs:ro  # read-only
    environment:
      - DATA_SOURCE=cowrie
      - COWRIE_LOG_PATH=/app/cowrie-logs/cowrie.json
```

### Pattern 4: Nginx Reverse Proxy for WebSocket + HTTPS

**What:** Single Nginx container handles TLS termination and routes traffic to frontend/backend.

**When to use:** Production deployment with HTTPS and WebSocket support.

**Trade-offs:**
- Pro: Standard production practice
- Pro: Handles WebSocket upgrade correctly
- Pro: Static file serving (Next.js build) can be optimized
- Con: Extra container and configuration

**Example (nginx.conf):**
```nginx
server {
    listen 443 ssl;
    server_name holding-cell.example.com;

    ssl_certificate /etc/letsencrypt/live/holding-cell.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/holding-cell.example.com/privkey.pem;

    # Frontend (Next.js)
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/;
    }

    # WebSocket (Socket.io)
    location /socket.io/ {
        proxy_pass http://backend:8000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;  # Long-lived connections
    }
}

# HTTP redirect to HTTPS
server {
    listen 80;
    server_name holding-cell.example.com;
    return 301 https://$server_name$request_uri;
}
```

## Data Flow

### Development Flow (Fake Data)

```
[AttackEmitter (asyncio task)]
    ↓ generate_fake_attack() every 3-8 seconds
[AttackEvent (Pydantic model)]
    ↓ sio.emit('attack_event', event)
[Frontend Socket.io client]
    ↓ receives attack_event
[JailCellGrid + StatsPanel]
```

### Production Flow (Real Cowrie Data)

```
[Attacker SSH/Telnet]
    ↓ connects to port 22/23
[Cowrie Honeypot]
    ↓ appends JSON line to cowrie.json
[Docker Volume (shared)]
    ↓
[Watchdog FileSystemEventHandler]
    ↓ reads new lines, parses JSON
[CowrieToAttackEvent adapter]
    ↓ classifies archetype, enriches with GeoIP
[AttackEvent (Pydantic model)]
    ↓ asyncio.run_coroutine_threadsafe(sio.emit(...))
[Frontend Socket.io client]
    ↓ receives attack_event
[JailCellGrid + StatsPanel]
```

### Cowrie Event to AttackEvent Mapping

| Cowrie Event | AttackEvent Fields | Notes |
|--------------|-------------------|-------|
| `cowrie.session.connect` | ip, port, timestamp, protocol | New session started |
| `cowrie.login.failed` | ip, commands (username/password attempts) | Brute force attempts |
| `cowrie.login.success` | ip, commands (successful credentials) | Successful login |
| `cowrie.command.input` | commands | Commands executed in session |
| `cowrie.session.closed` | duration | Session ended, calculate total |

### AttackEvent Field Mapping from Cowrie JSON

```python
def cowrie_to_attack_event(cowrie_event: dict) -> AttackEvent:
    """Convert Cowrie JSON event to AttackEvent."""
    # Base fields (present in all events)
    ip = cowrie_event.get("src_ip", "unknown")
    timestamp = cowrie_event.get("timestamp", datetime.utcnow().isoformat())
    session_id = cowrie_event.get("session", "")

    # Protocol detection
    protocol = "SSH" if cowrie_event.get("protocol") == "ssh" else "Telnet"

    # Port from dst_port or default
    port = cowrie_event.get("dst_port", 22)

    # Classify archetype from session behavior
    archetype = classify_archetype_from_session(cowrie_event)

    # GeoIP lookup (can use MaxMind or ip-api.com)
    country, country_code = get_country_from_ip(ip)

    # Commands from session (varies by event type)
    commands = extract_commands_from_event(cowrie_event)

    # Duration from session closed event
    duration = calculate_duration(cowrie_event)

    return create_attack_event(
        ip=ip,
        country=country,
        countryCode=country_code,
        port=port,
        protocol=protocol,
        archetype=archetype,
        commands=commands,
        duration=duration,
        rawLog=json.dumps(cowrie_event)
    )
```

### Session-based Classification

Cowrie events are session-based. To classify archetypes correctly, you must correlate events by session ID:

```
1. cowrie.session.connect (src_ip, src_port, dst_port) → Start session
2. cowrie.login.failed (username, password) → Brute force attempts
3. cowrie.command.input (input) → Commands executed
4. cowrie.session.closed (duration) → End session, emit final AttackEvent
```

**Recommendation:** Maintain an in-memory session cache that accumulates events by session ID, then emits a complete AttackEvent when `cowrie.session.closed` is received.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Demo/Portfolio (0-100 connections) | Single VPS, Docker Compose, sufficient |
| Higher traffic (100-1000) | Add rate limiting in Nginx, consider Redis for Socket.io |
| Production monitoring | Add Prometheus/Grafana containers for metrics |

### Scaling Priorities

1. **First bottleneck:** WebSocket connections - Socket.io handles well, but may need Redis adapter for multi-backend scaling
2. **Second bottleneck:** Cowrie log file I/O - Consider batching events if file grows large
3. **Third bottleneck:** TLS termination - Nginx handles this well; no changes needed until very high load

## Anti-Patterns

### Anti-Pattern 1: Synchronous File Reading in Async Context

**What people do:** Read entire cowrie.json file on each event.

**Why it's wrong:** Blocks event loop, causes WebSocket lag, O(n) file size.

**Do this instead:** Track file position, read only new lines (tail -f pattern).

```python
# BAD - blocks event loop
with open('cowrie.json') as f:
    events = json.loads(f.read())  # Blocks!

# GOOD - incremental read
def _read_new_events(self, path):
    with open(path, 'r') as f:
        f.seek(self.last_position)  # Resume from last read
        new_lines = f.readlines()
        self.last_position = f.tell()
    return [json.loads(line) for line in new_lines if line.strip()]
```

### Anti-Pattern 2: Exposing Cowrie Directly to Internet

**What people do:** Run Cowrie on default ports 22/23 without firewall rules.

**Why it's wrong:** Real SSH server conflicts; security risk if Cowrie has vulnerabilities.

**Do this instead:** Move real SSH to alternate port (22222), use firewall rules, run Cowrie in isolated Docker network.

```bash
# Move real SSH to alternate port
sudo sed -i 's/^#\?Port .*/Port 22222/' /etc/ssh/sshd_config
sudo ufw allow 22222/tcp
sudo systemctl reload ssh
```

### Anti-Pattern 3: Missing TLS for WebSocket

**What people do:** Configure WebSocket without considering HTTPS/WSS.

**Why it's wrong:** Mixed content errors; browsers block ws:// from https:// pages.

**Do this instead:** Nginx terminates TLS, proxies WebSocket upgrade to backend.

### Anti-Pattern 4: Hot Reloading with Volume Mounts in Production

**What people do:** Use development-style volume mounts for code in production.

**Why it's wrong:** Security risk, performance overhead, unintended code updates.

**Do this instead:** Production builds copy code into image; no volume mounts for app code.

### Anti-Pattern 5: Blocking Port 80

**What people do:** Block port 80 for security.

**Why it's wrong:** Let's Encrypt ACME HTTP-01 challenges require port 80.

**Do this instead:** Keep port 80 open, redirect to HTTPS. Configure Nginx to serve ACME challenge responses.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **Cowrie Honeypot** | Docker volume shared log file | `/var/log/cowrie/cowrie.json` |
| **GeoIP lookup** | httpx async API call (optional) | Can use MaxMind GeoIP2 or ip-api.com |
| **Let's Encrypt** | Certbot in Nginx container | Auto-renewal via cron or Certbot sidecar |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ Backend | Socket.io WebSocket | Existing implementation |
| Backend ↔ Cowrie logs | Docker volume (file read) | Shared volume read-only for backend |
| Nginx ↔ Frontend | HTTP proxy | Static Next.js build |
| Nginx ↔ Backend | HTTP proxy + WebSocket upgrade | Socket.io requires upgrade header |

### Docker Compose Service Dependencies

```yaml
services:
  nginx:
    depends_on:
      - frontend
      - backend
    ports:
      - "80:80"
      - "443:443"

  frontend:
    depends_on:
      - backend

  backend:
    depends_on:
      - cowrie  # Wait for log volume to exist
    environment:
      - DATA_SOURCE=cowrie

  cowrie:
    # No depends_on - standalone honeypot
    ports:
      - "22:2222"
      - "23:2223"
```

## Sources

- [Cowrie Official Documentation](https://docs.cowrie.org/en/stable/README.html) - HIGH confidence
- [Cowrie Docker Hub](https://hub.docker.com/r/cowrie/cowrie) - HIGH confidence
- [Cowrie Output Event Reference](https://docs.cowrie.org/en/latest/OUTPUT.html) - HIGH confidence
- [python-socketio AsyncServer Documentation](https://python-socketio.readthedocs.io/en/v4/server.html) - HIGH confidence
- [Watchdog + FastAPI Integration](https://lifetechia.com/python-automation-with-watchdog-and-fastapi/) - MEDIUM confidence
- [Nginx + Docker + Let's Encrypt Architecture](https://blog.devops.dev/nginx-docker-lets-encrypt-a-battle-tested-reverse-proxy-architecture-91d8e9ed7f9d) - MEDIUM confidence
- [Docker Compose FastAPI Next.js Boilerplate](https://dev.to/nkz21/i-built-a-production-ready-nextjs-14-fastapi-docker-boilerplate-free-pro-version-3ln0) - MEDIUM confidence
- [Cowrie JSON Log Analysis](https://defrancisco.us/blog/index.php/2023/07/29/understanding-the-cowrie-feed/) - MEDIUM confidence

---

*Architecture research for: SOC / Threat Intelligence Visualization Dashboard + Cowrie Integration*
*Researched: 2026-03-26 (Updated for Milestone v1.1)*