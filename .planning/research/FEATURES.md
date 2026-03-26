# Feature Research: SOC / Threat Intelligence Dashboard

**Domain:** Security Operations Center (SOC) dashboard with real-time honeypot attack visualization
**Researched:** 2026-03-26 (updated for Cowrie honeypot + Docker deployment)
**Confidence:** HIGH

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels broken or incomplete. For a SOC/threat intelligence dashboard, these are non-negotiable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Real-time attack feed** | Core value proposition. Users need to see attacks as they happen. | MEDIUM | Socket.io/WebSocket is the standard approach. SSE is simpler but less bidirectional. |
| **Attack count statistics** | Immediate situational awareness. "How active are we?" | LOW | Simple counters that increment on each event. |
| **Geographic origin visualization** | Attackers come from somewhere. Country/IP context is fundamental. | MEDIUM | Country flags, world map heat, or origin list. |
| **Attack type / archetype classification** | Not all attacks are equal. Classification enables understanding threat landscape. | MEDIUM | Requires behavioral rules or ML. For fake data: archetype-based rules are sufficient. |
| **Connection status indicator** | Users must know if the feed is live or disconnected. | LOW | "LIVE" badge, connection state, auto-reconnect behavior. |
| **Dark mode** | SOC analysts work in low-light environments. Dark is the default expectation. | LOW | Explicit requirement per DESIGN.md. |
| **Responsive layout** | Users view dashboards on different screen sizes. | LOW | Grid-based layouts handle this naturally. |
| **Persistent container deployment** | Production honeypots run 24/7. | MEDIUM | Docker Compose with restart policies. |
| **HTTPS access** | Security standard for public-facing apps. | MEDIUM | Nginx + Let's Encrypt Certbot. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but memorable and impressive. This is where The Holding Cell's gamified pixel-art concept lives.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Gamified attack visualization (jail cell metaphor)** | Visually memorable. Transforms abstract threat data into theatrical experience. Stops recruiters from scrolling past. | MEDIUM | Core differentiator. Pixel-art prisoner animation is the "wow moment." |
| **Animated prisoner entrance (Framer Motion spring physics)** | Delight and demonstrate skill. Shows real-time data handling + animation competence. | MEDIUM | Physics-based spring animation. Bounce on landing creates organic feel. |
| **Attacker archetype fingerprinting** | Educational. Shows you understand threat categories, not just raw counts. | MEDIUM | script_kiddie, botnet_drone, apt_operative, iot_worm, hacktivist archetypes with distinct fingerprints. |
| **Hover-to-reveal arrest record** | Information on demand. Keeps UI clean while allowing deep dives. | LOW | Tooltip with IP, country, protocol, archetype, timestamp. Retro terminal aesthetic. |
| **Real Cowrie honeypot data** | Live threat intelligence. Shows real attacks from the internet, not simulated. | MEDIUM | Cowrie JSON log tailing + real-time Socket.io bridge. |
| **Docker Compose one-command deploy** | Easy deployment. Demonstrates DevOps competence. | MEDIUM | Single `docker-compose up` runs everything. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems for this project specifically.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Full packet capture / raw log viewer** | Sounds like "more data = more impressive." | Storage, complexity, and privacy issues. Fake data doesn't benefit from this. | Raw log string in arrest record tooltip is sufficient for MVP. |
| **Real user authentication / login system** | "Real products have auth." | Adds infrastructure complexity. This is a portfolio demo, not an enterprise product. | None needed for MVP. Consider simple password gate only if demo requires it. |
| **Storing actual malware** | "Let's analyze downloaded files." | Security risk, legal liability in portfolio project. | Store hash + filename only, discard binary. |
| **Direct honeypot control from dashboard** | "Let users ban IPs from dashboard." | Attack surface, breaks demo simplicity. | Read-only honeypot integration. |
| **Historical attack database** | "Show trends over time." | Scope creep, database complexity. | Stream-only, no persistence (or defer to v2). |
| **Multi-honeypot aggregation (Cowrie + Dionaea + T-Pot simultaneously)** | "More sources = more impressive." | Weekend 2 scope is single Cowrie integration. Premature optimization. | Single honeypot source, done well. |
| **Full SIEM integration (Splunk, QRadar connectors)** | "Real SOCs have SIEMs." | Defeats the portfolio demo purpose. Over-engineering. | Standalone demo with simulated data is the point. |

---

## Cowrie Honeypot Integration

### Attack Data Available

Cowrie produces structured JSON events. Key data points for The Holding Cell:

| Event Type | Description | Key Fields | Use in Dashboard |
|------------|-------------|------------|------------------|
| `cowrie.session.connect` | New connection | `src_ip`, `src_port`, `dst_ip`, `dst_port` | Create new prisoner avatar |
| `cowrie.login.success` | Successful auth | `username`, `password` | Successful breach (rare, high severity) |
| `cowrie.login.failed` | Failed auth | `username`, `password` | Brute force indicator, feed stats |
| `cowrie.command.input` | Shell command | `input` | Behavior analysis for archetype |
| `cowrie.session.file_upload` | Attacker uploads file | `filename`, `shasum` | Malware drop indicator |
| `cowrie.session.file_download` | Attacker downloads file | `url`, `shasum` | Botnet malware fetch |
| `cowrie.client.version` | SSH client info | `version` | Client fingerprinting |
| `cowrie.client.kex` | SSH fingerprint | `hassh`, `kexAlgs`, `keyAlgs` | Archetype classification |

### Archetype Classification from Cowrie Data

Use Cowrie's HASSH fingerprint + behavior patterns to classify attacks into existing 5 archetypes:

| Archetype | Cowrie Indicators | Classification Rules |
|-----------|-------------------|---------------------|
| `script_kiddie` | Common passwords (`admin`, `123456`), default SSH client (`PuTTY`, `libssh`) | Low-skill credential stuffing |
| `botnet_drone` | Repeated connections, automated commands (`wget`, `curl`, `chmod +x`), malware downloads | Automated behavior patterns, IoT-focused |
| `apt_operative` | Unusual SSH client fingerprint, custom commands, persistence attempts (`crontab`, `rc.local`) | HASSH fingerprint + sophisticated commands |
| `iot_worm` | IoT-specific credentials (`admin/admin`, `root/root`), binary downloads targeting ARM/MIPS | Device-targeted credentials + architecture-specific binaries |
| `hacktivist` | Political commands, defacement attempts, website reconnaissance | Command content analysis for intent |

### Integration Architecture

```
Internet Attackers
       │
       ▼
   Cowrie (Docker)
   SSH :22  Telnet :23
       │
       │ JSON log
       ▼
   /cowrie/var/log/cowrie/cowrie.json
       │
       │ Docker volume mount
       ▼
   Python Backend (FastAPI)
       │
       │ Log tail + parse
       ├──► Event classification (archetype)
       └──► Socket.io emit
              │
              ▼
   Next.js Frontend
   JailCellGrid + StatsPanel
```

### Real-World Attack Data (2025 Study)

From [Running a Cowrie Honeypot: Data and Findings](https://ambientnode.uk/running-a-cowrie-honeypot-data-and-findings/):

- **89,109 events** across **20,683 sessions** in 11 days
- **2,123 unique attacker IPs**
- **75.6% SSH** / **24.4% Telnet** sessions
- Top usernames: `admin`, `root`, `user`
- Top passwords: `123456`, `root`, `abc123`

---

## Docker Compose Deployment

### Service Architecture

| Service | Port | Purpose | Dependencies |
|---------|------|---------|--------------|
| `cowrie` | 22:2222, 23:2223 | SSH/Telnet honeypot | None |
| `backend` | 8000 | FastAPI + Socket.io | Cowrie volume mount |
| `frontend` | 3000 | Next.js dashboard | Backend Socket.io |
| `nginx` | 80, 443 | Reverse proxy + HTTPS | Frontend, Backend |

### Required Docker Compose Configuration

```yaml
services:
  cowrie:
    image: cowrie/cowrie:latest
    ports:
      - "22:2222"    # SSH
      - "23:2223"    # Telnet (optional)
    environment:
      - COWRIE_TELNET_ENABLED=yes
    volumes:
      - cowrie-var:/cowrie/cowrie-git/var
    restart: always

  backend:
    build: ./backend
    volumes:
      - cowrie-var:/cowrie-data:ro  # Read Cowrie logs
    depends_on:
      - cowrie
    restart: always

  frontend:
    build: ./frontend
    depends_on:
      - backend
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - letsencrypt:/etc/letsencrypt
    depends_on:
      - frontend
      - backend
    restart: always

volumes:
  cowrie-var:
  letsencrypt:
```

### HTTPS with Let's Encrypt

Use Certbot with standalone mode or Nginx integration:

1. **Initial certificate**: `certbot certonly --standalone -d yourdomain.com`
2. **Auto-renewal**: `certbot renew` in cron or Docker sidecar
3. **Nginx routes**:
   - `/` -> Next.js frontend (port 3000)
   - `/socket.io` -> Backend (port 8000) -- **requires sticky sessions for WebSocket**
   - `/api` -> FastAPI backend (port 8000)

### WebSocket Sticky Sessions

Critical for Socket.io: Nginx must use sticky sessions (ip_hash) to route all WebSocket connections from same client to same backend instance.

```nginx
upstream backend {
    ip_hash;  # Sticky sessions for WebSocket
    server backend:8000;
}
```

---

## Feature Dependencies

```
Cowrie JSON Log Access
    └──requires──> Docker volume mount (cowrie-var)
                       └──requires──> Backend file read permission

Archetype Classification
    └──requires──> Cowrie HASSH fingerprint data
    └──requires──> Command input analysis
    └──requires──> Existing BACK-08 classification rules (already implemented)

Socket.io Real-time
    └──requires──> Nginx sticky sessions (WebSocket)
    └──requires──> Backend Cowrie log tail process

HTTPS Access
    └──requires──> Domain pointed to VPS
    └──requires──> Certbot certificate
    └──requires──> Nginx reverse proxy
```

### Dependency Notes

- **Cowrie JSON Log Access requires Docker volume mount:** Backend needs read access to `/cowrie/cowrie-git/var/log/cowrie/cowrie.json`. Use shared Docker volume between Cowrie and Backend containers.
- **Archetype Classification requires HASSH fingerprint:** Cowrie's `cowrie.client.kex` event provides `hassh` field for SSH client fingerprinting. Use this + command patterns to classify.
- **Socket.io requires Nginx sticky sessions:** WebSocket connections break without session affinity. Use `ip_hash` in Nginx upstream.
- **HTTPS requires Domain first:** Let's Encrypt won't issue for IP addresses. Must have domain configured and pointed to VPS before certificate request.

---

## MVP Definition

### Launch With (v1.0 - Fake Data) -- COMPLETE

- [x] **Real-time attack feed via Socket.io** -- The core pipeline. Everything else depends on this.
- [x] **Attack count statistics (StatsPanel)** -- Situational awareness.
- [x] **Gamified jail cell visualization with pixel-art prisoners** -- The core differentiator.
- [x] **Animated prisoner entrance (spring physics)** -- The wow moment.
- [x] **Hover arrest record tooltip** -- Detail on demand.
- [x] **Attack archetype classification (5 types)** -- Already implemented with BACK-08 rules.
- [x] **Connection status indicator ("LIVE" badge)** -- Analyst knows if feed is alive.
- [x] **Dark retro-futuristic aesthetic** -- Per DESIGN.md.
- [x] **Responsive layout + light/dark mode** -- Validated in Phase 04.

### Launch With (v1.1 - Real Threats) -- IN PROGRESS

- [ ] **Cowrie log tailing** -- Python process tails Cowrie JSON log, parses events
- [ ] **Event parsing** -- Extract src_ip, username, password, command from Cowrie events
- [ ] **Archetype classification from real data** -- Map Cowrie data to existing 5 archetypes
- [ ] **Socket.io bridge** -- Emit parsed attacks to frontend in real-time
- [ ] **Docker Compose orchestration** -- Single `docker-compose up` deploys everything
- [ ] **Nginx reverse proxy** -- Route traffic to frontend/backend/cowrie
- [ ] **HTTPS with Let's Encrypt** -- Secure public access on existing domain

### Add After Validation (v1.x)

Features to add once core integration works.

- [ ] **Geolocation enrichment** -- Enrich IP with GeoIP data (MaxMind database)
- [ ] **Attack statistics persistence** -- Store counts in SQLite/Redis for uptime stats
- [ ] **Attack replay** -- Show what commands attacker ran (TTY log parsing)

### Future Consideration (v2+)

Features to defer until concept proven.

- [ ] **Multi-sensor deployment** -- Multiple Cowrie instances feeding one dashboard
- [ ] **Historical analysis** -- Time-series charts, attack trends
- [ ] **SIEM integration** -- Export to Elasticsearch/Splunk
- [ ] **Alert notifications** -- Telegram/Discord alerts for notable attacks

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Cowrie log tailing | HIGH | LOW | P1 |
| Event parsing + classification | HIGH | MEDIUM | P1 |
| Docker Compose setup | HIGH | MEDIUM | P1 |
| Nginx + HTTPS | HIGH | MEDIUM | P1 |
| Geolocation enrichment | MEDIUM | LOW | P2 |
| Attack statistics persistence | MEDIUM | LOW | P2 |
| TTY log replay | LOW | HIGH | P3 |
| Multi-sensor support | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for v1.1 launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## Implementation Complexity Notes

### Low Complexity (Same Day)
- Docker Compose file for existing services
- Cowrie environment variable configuration (`COWRIE_TELNET_ENABLED=yes`)
- Backend log file reading (file tail)
- Nginx configuration for reverse proxy

### Medium Complexity (1-2 Days)
- Nginx reverse proxy configuration with WebSocket sticky sessions
- Let's Encrypt certificate setup with auto-renewal
- Archetype classification logic from HASSH + behavior patterns
- Docker volume sharing between Cowrie and Backend

### High Complexity (3+ Days)
- TTY log replay (requires parsing Cowrie's binary session format)
- Multi-sensor coordination (architecture changes)
- Historical persistence (database schema, queries)

---

## Competitor Feature Analysis

| Feature | Splunk Enterprise Security | IBM QRadar | Microsoft Sentinel | The Holding Cell |
|---------|---------------------------|------------|--------------------|--------------------|
| Real-time feed | YES (Splunk Stream) | YES (QRadar offenses) | YES (KQL streaming) | YES (Socket.io) |
| Attack statistics | YES (KPIs, dashboards) | YES (offense counts) | YES (workbooks) | YES (StatsPanel) |
| Geographic origin | YES (IP mapping app) | YES (geo lookup) | YES (IP enrichment) | Country flags only |
| Attack classification | YES (correlation rules) | YES (reference sets) | YES (analytics rules) | 5 archetypes |
| Visual/animation | NO (enterprise static) | NO (enterprise static) | NO (enterprise static) | YES (pixel-art animation) |
| Gamification | NO | NO | NO | YES (jail cell metaphor) |
| Honeypot native | NO | NO | NO | YES (Cowrie integration) |
| One-command deploy | NO | NO | NO | YES (Docker Compose) |
| Portfolio demo appeal | LOW | LOW | LOW | HIGH (unique) |

**Key insight:** Enterprise SOC tools (Splunk, QRadar, Sentinel) are powerful but visually boring. They are built for security operations, not for impressing recruiters. The Holding Cell's gamified pixel-art approach + real Cowrie honeypot data is a deliberate trade: less enterprise functionality, more memorability for a portfolio piece.

---

## Sources

### Cowrie Honeypot
- [Cowrie Output Event Code Reference](https://cowrie.readthedocs.io/en/latest/OUTPUT.html) -- HIGH confidence, official documentation
- [Cowrie Docker Repository](https://docs.cowrie.org/en/stable/docker/README.html) -- HIGH confidence, official documentation
- [Running a Cowrie Honeypot: Data and Findings](https://ambientnode.uk/running-a-cowrie-honeypot-data-and-findings/) -- MEDIUM confidence, case study with real data
- [Real-Time Cowrie Honeypot Alerts via Telegram](https://infosecwriteups.com/real-time-cowrie-honeypot-alerts-via-telegram-track-ssh-attacks-credentials-tools-instantly-58b95c61a56b) -- MEDIUM confidence, implementation patterns
- [Tr4pNode - Real-Time Visualization Project](https://github.com/ignacypolak1/tr4pnode) -- HIGH confidence, reference implementation

### Docker Deployment
- [Nginx + Docker + Let's Encrypt Architecture](https://blog.devops.dev/nginx-docker-lets-encrypt-a-battle-tested-reverse-proxy-architecture-91d8e9ed7f9d) -- MEDIUM confidence, community guide
- [Docker Official: Next.js with Compose & NGINX](https://docker.com/blog/how-to-build-and-run-next-js-applications-with-docker-compose-nginx) -- HIGH confidence, official Docker guide
- [Setting Up HTTPS with Docker Compose, Nginx, Certbot](https://medium.com/@dinusai05/setting-up-a-secure-reverse-proxy-with-https-using-docker-compose-nginx-and-certbot-lets-encrypt-cfd012c53ca0) -- MEDIUM confidence, tutorial
- [Production-Ready Next.js 14 + FastAPI + Docker Boilerplate](https://github.com/nkz21/nextjs-fastapi-docker-boilerplate) -- HIGH confidence, reference implementation

### Competitor Analysis
- Splunk Enterprise Security product documentation (training data)
- IBM QRadar documentation (training data)
- Microsoft Sentinel / Azure Sentinel documentation (training data)
- MISP (Open Source Threat Intelligence Platform) feature set (training data)

---

*Feature research for: SOC / Threat Intelligence Dashboard*
*Researched: 2026-03-26 (updated for Cowrie honeypot + Docker deployment)*