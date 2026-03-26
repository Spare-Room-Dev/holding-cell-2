# Pitfalls Research

**Domain:** Cowrie honeypot integration + Docker Compose deployment + VPS hosting for public-facing dashboard
**Researched:** 2026-03-26
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Running Cowrie as Root User

**What goes wrong:**
Cowrie honeypot is installed and runs as root, creating a catastrophic security vulnerability. If attackers discover a vulnerability in Cowrie itself or in its Python dependencies, they gain root access to the host system.

**Why it happens:**
Developers following quick-start guides that skip the dedicated user setup step, or using Docker containers that default to root without explicitly configuring a non-root user.

**How to avoid:**
Always create a dedicated low-privilege `cowrie` user:
```bash
sudo adduser --disabled-password --gecos 'Cowrie' cowrie
sudo su - cowrie
```
If using Docker, explicitly set `user: "1000:1000"` in docker-compose.yml.

**Warning signs:**
- `ps aux | grep cowrie` shows `root` as the process owner
- Docker containers run without `user` directive

**Phase to address:**
Phase 1 (Cowrie Integration Setup)

---

### Pitfall 2: Poor Network Isolation Between Honeypot and Backend

**What goes wrong:**
Cowrie honeypot is deployed on the same network as the backend/frontend services, or worse, has outbound internet access. Attackers can pivot from the honeypot to internal services, or use the honeypot as a launch point for attacks on other systems.

**Why it happens:**
Docker's default networking puts all containers on the same bridge network, and developers don't think to segment honeypot traffic from application traffic.

**How to avoid:**
Create isolated networks in docker-compose.yml:
```yaml
networks:
  honeypot:
    internal: true  # No outbound internet access
    driver: bridge
  app:
    driver: bridge

services:
  cowrie:
    networks:
      - honeypot
    # Block outbound at firewall level too
  backend:
    networks:
      - app
```
At the VPS level, use iptables to prevent outbound connections from Cowrie:
```bash
sudo iptables -A OUTPUT -p tcp --syn -m owner --uid-owner cowrie -j DROP
```

**Warning signs:**
- Cowrie can ping external IPs from within container
- Backend API accessible from Cowrie container

**Phase to address:**
Phase 1 (Cowrie Integration Setup)

---

### Pitfall 3: Exposing Dashboard Admin Interface Publicly

**What goes wrong:**
The honeypot dashboard is exposed to the entire internet at the same ports used for admin access, allowing attackers to view the very threat intelligence being collected against them.

**Why it happens:**
Default configurations often bind to `0.0.0.0`, and developers don't firewall restrict admin interfaces during setup.

**How to avoid:**
1. Use firewall rules to restrict dashboard access to your IP only:
```bash
# During setup - restrict everything
ufw allow from YOUR_IP to any port 64294:64297

# After deployment - allow honeypot ports from anywhere, admin only from your IP
ufw allow 22      # SSH (honeypot)
ufw allow 23      # Telnet (honeypot)
ufw allow from YOUR_IP to any port 3000  # Dashboard
ufw allow from YOUR_IP to any port 8000  # Backend API
```

2. Bind internal services to localhost:
```yaml
ports:
  - "127.0.0.1:8000:8000"  # Only localhost access
```

**Warning signs:**
- Dashboard accessible from any IP without authentication prompt
- Security groups allow all inbound traffic

**Phase to address:**
Phase 2 (VPS Deployment & Security)

---

### Pitfall 4: WebSocket Connection Drops Behind Nginx Reverse Proxy

**What goes wrong:**
Socket.io connections work locally but fail in production with HTTP 400 errors, "Session ID unknown" messages, or connections dropping after 60 seconds.

**Why it happens:**
Nginx's default proxy timeout (60s) is shorter than Socket.io's default ping interval (25s) + ping timeout (20s) = 45s. Additionally, the required WebSocket upgrade headers are missing.

**How to avoid:**
Configure Nginx with proper WebSocket support:
```nginx
location /socket.io/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;   # 1 hour - longer than any expected session
    proxy_send_timeout 3600s;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

**Warning signs:**
- HTTP 400 errors with "Session ID unknown" in browser console
- Connections work briefly then disconnect after 60 seconds
- Long-polling fallback activated (WebSocket upgrade failed)

**Phase to address:**
Phase 2 (VPS Deployment & Security)

---

### Pitfall 5: Using Default Bridge Network in Docker Compose

**What goes wrong:**
Services cannot communicate using service names, developers resort to `localhost` or IP addresses, and DNS-based service discovery fails entirely.

**Why it happens:**
Docker's default bridge network doesn't support DNS resolution between containers. Developers don't realize they need to define custom networks.

**How to avoid:**
Always define custom networks in docker-compose.yml:
```yaml
services:
  backend:
    networks:
      - app-network
  frontend:
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

Then reference services by name:
```javascript
// WRONG
const socket = io('http://localhost:8000');

// CORRECT
const socket = io('http://backend:8000');  // Inside Docker
const socket = io('https://yourdomain.com');  // From browser
```

**Warning signs:**
- `ECONNREFUSED 127.0.0.1:8000` errors in container logs
- `nslookup backend` returns no results inside container
- Using `network_mode: host` as a "fix" (breaks DNS entirely)

**Phase to address:**
Phase 2 (VPS Deployment & Security)

---

### Pitfall 6: Let's Encrypt Rate Limit Hit During Testing

**What goes wrong:**
Certificate issuance fails with rate limit errors after a few attempts, blocking production deployment for up to a week.

**Why it happens:**
Let's Encrypt enforces strict limits: 50 certificates per domain per week, 5 duplicate certificates per week, 5 failed validations per hour per hostname. Developers test in production without using the staging environment.

**How to avoid:**
Always use `--staging` or `--dry-run` for testing:
```bash
# Test with staging first
sudo certbot certonly --staging -d yourdomain.com --webroot -w /var/www/certbot

# Only use production when ready
sudo certbot certonly -d yourdomain.com --webroot -w /var/www/certbot
```

**Warning signs:**
- "too many certificates already issued" error
- "too many failed validations" error
- Testing against production domain repeatedly

**Phase to address:**
Phase 2 (VPS Deployment & Security)

---

### Pitfall 7: Hardcoded Secrets in Docker Compose Files

**What goes wrong:**
API keys, database passwords, and JWT secrets are committed to version control in docker-compose.yml or .env files, exposing credentials to anyone with repository access.

**Why it happens:**
It's the quickest path to "working" configuration, and developers forget to remove secrets before committing.

**How to avoid:**
1. Use `.env` files that are gitignored:
```bash
# .gitignore
.env
.env.local
.env.production
```

2. Reference secrets from environment:
```yaml
services:
  backend:
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - DATABASE_URL=${DATABASE_URL}
```

3. For production, use Docker secrets or external secret managers.

**Warning signs:**
- `docker inspect` shows plaintext passwords
- `.env` files visible in git status
- Secrets visible in Docker Hub layer history

**Phase to address:**
Phase 2 (VPS Deployment & Security)

---

### Pitfall 8: Missing Health Checks for Service Dependencies

**What goes wrong:**
Backend tries connecting to Cowrie log file before Cowrie starts, or frontend connects to backend before it's ready. Containers start but applications crash on first request.

**Why it happens:**
`depends_on` only waits for container to start, not for the application inside to be ready. The container is "running" but the Python app inside is still initializing.

**How to avoid:**
Define proper health checks:
```yaml
services:
  cowrie:
    healthcheck:
      test: ["CMD", "test", "-f", "/home/cowrie/cowrie/var/log/cowrie/cowrie.json"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  backend:
    depends_on:
      cowrie:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  frontend:
    depends_on:
      backend:
        condition: service_healthy
```

**Warning signs:**
- "Connection refused" errors in startup logs
- Services restart in loops despite depends_on
- Race conditions that only appear on slower machines

**Phase to address:**
Phase 2 (VPS Deployment & Security)

---

### Pitfall 9: SSH Port Conflict with Cowrie

**What goes wrong:**
Cowrie is configured to listen on port 22, but the VPS's real SSH service already uses that port. Either Cowrie fails to start, or administrators lock themselves out of the server.

**Why it happens:**
Quick-start guides assume port 22 for the honeypot, but on a real VPS you need SSH access for administration.

**How to avoid:**
1. Move real SSH to a non-standard port:
```bash
# Edit /etc/ssh/sshd_config
Port 22022
```

2. Update firewall rules before changing:
```bash
ufw allow 22022/tcp  # Add new SSH port first!
```

3. Configure Cowrie to use port 22:
```ini
# cowrie.cfg
[ssh]
listen_port = 2222
```

4. Redirect external port 22 to Cowrie:
```bash
iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
```

**Warning signs:**
- Cowrie fails with "Address already in use"
- SSH connection drops after starting Cowrie container
- Can't SSH into VPS after Cowrie deployment

**Phase to address:**
Phase 1 (Cowrie Integration Setup)

---

### Pitfall 10: FastAPI CORS Open to All Origins

**What goes wrong:**
CORS is configured with `allow_origins=["*"]` in production, allowing any website to make requests to the API and potentially extract honeypot data.

**Why it happens:**
Default development configurations use wildcard CORS for convenience, and developers forget to restrict it for production.

**How to avoid:**
Restrict CORS to specific origins:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origin only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**Warning signs:**
- Browser shows wildcard in Access-Control-Allow-Origin response
- API responds to requests from any domain
- Security scan flags CORS misconfiguration

**Phase to address:**
Phase 2 (VPS Deployment & Security)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Running as root in containers | Faster setup, fewer permission issues | Critical security vulnerability if compromised | Never acceptable for honeypot workloads |
| Hardcoded secrets in compose files | Works immediately | Credentials leak via git history | Never - use .env files from start |
| No health checks | Faster container startup | Race conditions, unreliable startup order | Never - define from day one |
| CORS wildcard `["*"]` | Works from any origin | Any site can access your API | Development only - restrict before deploy |
| Single Docker network for all services | Simpler configuration | Honeypot can access backend/frontend | Never acceptable - segment from day one |
| No log rotation | Easier debugging during development | Disk exhaustion, lost data | Development only - add rotation before production |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Cowrie logs | Parsing raw text instead of JSON | Use JSON log format: `output_format = json` |
| Cowrie to backend | Polling log file directly without rotation | Use file tailing with rotation support (watchdog) |
| Socket.io behind Nginx | Missing WebSocket upgrade headers | Include `proxy_set_header Upgrade` and `Connection "upgrade"` |
| Socket.io CORS | Frontend origin hardcode vs environment variable | Use `FRONTEND_URL` environment variable |
| Docker networking | Using `localhost` inside containers | Use service names (`backend`, `frontend`) |
| Let's Encrypt | Testing against production | Always use `--staging` first |
| Certbot renewal | Nginx not reloading after cert renewal | Create renewal deploy hook |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Single Uvicorn worker in production | Crashes under load, slow responses | Use Gunicorn with multiple workers: `gunicorn -k uvicorn.workers.UvicornWorker -w 4` | 10+ concurrent connections |
| Default Nginx proxy timeout (60s) | WebSocket disconnects after 60s | Set `proxy_read_timeout 3600s` | Long-running dashboard sessions |
| No log rotation for Cowrie | Disk fills with JSON logs | Configure `logrotate` or set max log size | Days/weeks depending on attack volume |
| Database connection pool exhaustion | Connection timeouts under load | Set `pool_size=20, max_overflow=30` for async engine | Depends on concurrent request volume |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Running Cowrie as root | Root access if honeypot compromised | Dedicated `cowrie` user with minimal permissions |
| Honeypot on same network as app | Lateral movement from honeypot to dashboard | Separate Docker networks, firewall rules blocking outbound |
| Dashboard on public internet | Attackers view threat intel about themselves | IP-restricted firewall rules, HTTP Basic Auth |
| Wildcard CORS | Any website can access your API | Restrict to `https://yourdomain.com` |
| Hardcoded secrets in git | Credential leak via version control | `.env` files in `.gitignore`, Docker secrets in production |
| No rate limiting on API | API spam causing crashes | Implement `slowapi` or similar rate limiting |
| Missing HTTPS | MITM attacks, credential interception | Let's Encrypt Certbot with auto-renewal |
| SSH still on port 22 | SSH lockout when Cowrie takes port | Move SSH to alternate port, iptables redirect |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Dashboard downtime when Cowrie restarts | Real-time data stops, users confused | Show connection status indicator with auto-reconnect |
| No attack count reset option | Numbers keep growing indefinitely | Add "Clear session" or time-based counters |
| Generic error messages | Users don't know if it's their network or the server | Specific error states: "Connecting...", "Connected", "Disconnected - retrying" |
| No demo mode without honeypot | Can't demonstrate dashboard to recruiters without live data | Include simulated attack mode toggle |

## "Looks Done But Isn't" Checklist

- [ ] **Docker Compose:** Often missing health checks — verify services can actually start in dependency order
- [ ] **HTTPS:** Often missing auto-renewal hook — verify Certbot timer is active: `systemctl status certbot.timer`
- [ ] **Cowrie Integration:** Often missing log rotation — verify logrotate config exists for `/var/log/cowrie/`
- [ ] **WebSocket:** Often missing Nginx upgrade headers — test with real browser, not curl
- [ ] **Network Isolation:** Often missing firewall rules — verify Cowrie container cannot reach backend API
- [ ] **CORS:** Often still wildcard in production — test API call from your domain, check response headers

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Root user for Cowrie | MEDIUM | Create cowrie user, chown all files, restart service |
| Exposed dashboard | LOW | Add firewall rules immediately, add HTTP Basic Auth |
| WebSocket behind Nginx | LOW | Add upgrade headers, reload Nginx |
| Rate limited by Let's Encrypt | HIGH (wait time) | Wait 7 days, or use staging cert temporarily, then renew |
| Secrets in git history | HIGH | Rotate all secrets, use BFG or git-filter-branch to remove from history |
| No health checks | MEDIUM | Add health checks, restart services, test startup order |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Running Cowrie as root | Phase 1 (Cowrie Integration) | `ps aux \| grep cowrie` shows non-root user |
| Poor network isolation | Phase 1 (Cowrie Integration) | `docker exec cowrie ping backend` fails |
| Exposed dashboard | Phase 2 (VPS Deployment) | nmap from external IP shows only ports 22, 23, 443 |
| WebSocket drops | Phase 2 (VPS Deployment) | Dashboard stays connected for 5+ minutes |
| Default bridge network | Phase 2 (VPS Deployment) | `docker exec backend ping frontend` works |
| Let's Encrypt rate limit | Phase 2 (VPS Deployment) | `certbot certificates` shows valid cert, not rate-limited |
| Hardcoded secrets | Phase 2 (VPS Deployment) | `git grep -i password` returns nothing |
| Missing health checks | Phase 2 (VPS Deployment) | `docker-compose restart` brings all services up in correct order |
| SSH port conflict | Phase 1 (Cowrie Integration) | SSH works on alternate port, Cowrie captures port 22 |
| CORS misconfiguration | Phase 2 (VPS Deployment) | API responds with specific origin, not wildcard |

## Sources

- [Cowrie honeypot integration with Microsoft Sentinel](https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/cowrie-honeypot-and-its-integration-with-microsoft-sentinel/ba-p/4258349) - HIGH confidence (official Microsoft documentation)
- [Cowrie Output Event Code Reference](https://cowrie.readthedocs.io/en/latest/OUTPUT.html) - HIGH confidence (official Cowrie docs)
- [T-Pot Honeypot VPS Guide](https://medium.com/@satyampathania69/t-pot-honeypot-setup-ultimate-vps-guide-and-documentation-for-cybersecurity-students-a05b351bfd96) - MEDIUM confidence (community guide)
- [Docker Compose Security Crisis 2025](https://www.blog.brightcoding.dev/2025/11/10/docker-compose-security-crisis-how-declarative-configurations-became-your-biggest-risk-and-how-to-fix-it) - HIGH confidence (recent security analysis)
- [5 Docker Compose Mistakes That Break Production](https://dataquestio.medium.com/5-docker-compose-mistakes-that-will-break-your-production-pipeline-and-how-to-fix-them-5afe2ee68927) - MEDIUM confidence (community article)
- [Docker Compose Networking Common Mistakes](https://www.xda-developers.com/this-one-docker-compose-mistake-silently-breaks-your-networking/) - HIGH confidence (specific technical issue)
- [Socket.IO Troubleshooting Connection Issues](https://socket.io/docs/v4/troubleshooting-connection-issues) - HIGH confidence (official Socket.IO docs)
- [Common Socket.io Mistakes](https://moldstud.com/articles/p-common-pitfalls-when-using-socketio-and-how-to-avoid-them-essential-tips-for-developers) - MEDIUM confidence (community article)
- [Let's Encrypt Certbot Nginx Guide 2025](https://dev.to/addwebsolutionpvtltd/ssltls-certificates-with-certbot-and-nginx-the-2025-guide-57p3) - HIGH confidence (current best practices)
- [FastAPI Production Deployment Mistakes](https://mind-to-machine.medium.com/fastapi-in-production-7-mistakes-that-cost-me-and-how-i-fixed-them-5f22d5f3a3fd) - MEDIUM confidence (experience-based article)
- [6 FastAPI Deployment Mistakes](https://levelup.gitconnected.com/6-fastapi-deployment-mistakes-that-almost-broke-my-app-e53425292a4c) - MEDIUM confidence (experience-based article)

---
*Pitfalls research for: Cowrie honeypot + Docker deployment + VPS hosting*
*Researched: 2026-03-26*