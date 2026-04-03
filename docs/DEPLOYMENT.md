# Hetzner VPS Deployment Guide

Complete step-by-step guide to deploy The Holding Cell honeypot visualization system to a Hetzner VPS.

---

## Prerequisites

- Hetzner Cloud account
- Domain name with DNS A record pointing to server IP
- Local machine with SSH access

---

## Phase 1: Create Hetzner Server

### 1.1 Create Server

1. Log into [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Click **Add Server**
3. Configure:
   - **Location**: Choose closest to your target attackers
   - **Type**: CX22 (2 vCPU, 4 GB RAM, 40 GB disk) - minimum recommended
   - **Image**: Ubuntu 24.04 (or 22.04)
   - **SSH Key**: Add your public SSH key (`~/.ssh/id_rsa.pub`)
4. Click **Create & Buy Now**

### 1.2 Note Your Server Details

```
Server IP: <YOUR_SERVER_IP>
Root User: root
SSH Key: <your-ssh-key>
```

---

## Phase 2: Initial Server Setup

### 2.1 SSH into Server

```bash
ssh root@<YOUR_SERVER_IP>
```

### 2.2 Create Admin User

```bash
# Create user
adduser admin
usermod -aG sudo admin

# Copy SSH key for admin
mkdir -p /home/admin/.ssh
cp /root/.ssh/authorized_keys /home/admin/.ssh/
chown -R admin:admin /home/admin/.ssh
chmod 700 /home/admin/.ssh
chmod 600 /home/admin/.ssh/authorized_keys
```

### 2.3 Configure SSH on Port 2244

```bash
# Edit SSH config
nano /etc/ssh/sshd_config

# Change these lines:
Port 2244
PermitRootLogin no
PasswordAuthentication no

# Restart SSH
systemctl restart sshd
```

**CRITICAL:** Test connection in a NEW terminal before closing this one:

```bash
ssh -p 2244 admin@<YOUR_SERVER_IP>
```

### 2.4 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.5 Set Hostname

```bash
sudo hostnamectl set-hostname holding-cell
echo "127.0.1.1 holding-cell" | sudo tee -a /etc/hosts
```

---

## Phase 3: Install Docker

### 3.1 Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add admin user to docker group
sudo usermod -aG docker admin

# Install Docker Compose plugin
sudo apt install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 3.2 Start Docker

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

## Phase 4: Configure Firewall (UFW)

### 4.1 Run UFW Setup Script

Copy the project's UFW setup script:

```bash
# On local machine, from project root:
scp -P 2244 deploy/setup-ufw.sh admin@<YOUR_SERVER_IP>:/home/admin/

# SSH into server
ssh -p 2244 admin@<YOUR_SERVER_IP>

# Run the script
chmod +x setup-ufw.sh
sudo ./setup-ufw.sh
```

This configures:
- Port 2244: Admin SSH
- Port 22: Cowrie SSH honeypot (public)
- Port 23: Cowrie Telnet honeypot (public)
- Port 80: HTTP (Let's Encrypt challenges)
- Port 443: HTTPS (dashboard)

---

## Phase 5: Deploy Application

### 5.1 Clone Repository

```bash
# Option A: Clone from Git (recommended)
cd /home/admin
git clone <your-repo-url> holding-cell
cd holding-cell

# Option B: Copy from local machine (if not in git)
# On local machine:
scp -P 2244 -r "/path/to/Holding Cell 2" admin@<YOUR_SERVER_IP>:/home/admin/holding-cell
```

### 5.2 Create Environment File

```bash
cd /home/admin/holding-cell

# Create .env from example
cp .env.example .env
nano .env
```

### 5.3 Configure Environment Variables

```bash
# .env configuration
# Ports
FRONTEND_PORT=80
BACKEND_PORT=8000
COWRIE_SSH_PORT=2222
COWRIE_TELNET_PORT=2323

# Service names (do not change)
BACKEND_HOST=backend
FRONTEND_HOST=frontend
NGINX_HOST=nginx
COWRIE_HOST=cowrie

# Volume paths
COWRIE_LOG_PATH=/var/log/cowrie

# Domain name (REQUIRED for SSL)
DOMAIN=your-domain.com

# Admin credentials (used by setup-htpasswd.sh)
ADMIN_USER=admin

# WebSocket Authentication (per SEC-02)
# Generate with: openssl rand -hex 32
WEBSOCKET_AUTH_TOKEN=your-secure-token-here

# Certificate paths
CERT_PATH=/etc/letsencrypt/live
```

### 5.4 Generate WebSocket Auth Token

```bash
# Generate secure token and add to .env
TOKEN=$(openssl rand -hex 32)
echo "WEBSOCKET_AUTH_TOKEN=$TOKEN" >> .env
echo "Generated token: $TOKEN"
```

---

## Phase 6: Configure SSL Certificate

### 6.1 Install Certbot

```bash
sudo apt install -y certbot
```

### 6.2 Obtain SSL Certificate

```bash
# Stop nginx if running
docker compose down nginx 2>/dev/null || true

# Obtain certificate (standalone mode)
sudo certbot certonly --standalone \
  --preferred-challenges http \
  -d your-domain.com

# Follow prompts:
# - Enter email for notifications
# - Agree to terms
# - Optionally share email
```

### 6.3 Set Up Auto-Renewal

```bash
# Copy renewal service files
sudo cp deploy/certbot-renew.service /etc/systemd/system/
sudo cp deploy/certbot-renew.timer /etc/systemd/system/

# Update path in service file
sudo sed -i "s|/opt/holding-cell|/home/admin/holding-cell|g" /etc/systemd/system/certbot-renew.service

# Enable timer
sudo systemctl daemon-reload
sudo systemctl enable certbot-renew.timer
sudo systemctl start certbot-renew.timer
```

---

## Phase 7: Configure HTTP Basic Auth

### 7.1 Run htpasswd Setup

```bash
cd /home/admin/holding-cell

# Copy script to server (if not already)
scp -P 2244 deploy/setup-htpasswd.sh admin@<YOUR_SERVER_IP>:/home/admin/

# Run the script
chmod +x setup-htpasswd.sh
sudo ./setup-htpasswd.sh

# Enter admin password when prompted
```

---

## Phase 8: Configure GeoIP Database

### 8.1 Download MaxMind GeoLite2

```bash
# Create geoip directory
mkdir -p /home/admin/holding-cell/geoip

# Option A: Download from MaxMind (requires free account)
# 1. Create account at https://www.maxmind.com/en/geolite2/signup
# 2. Download GeoLite2-Country.mmdb
# 3. Upload to server:
scp -P 2244 GeoLite2-Country.mmdb admin@<YOUR_SERVER_IP>:/home/admin/holding-cell/geoip/

# Option B: Use geoipupdate (requires license key)
sudo apt install -y geoipupdate
# Configure /etc/geoip/geoip.conf with your license key
sudo geoipupdate
```

### 8.2 Verify GeoIP File

```bash
ls -la /home/admin/holding-cell/geoip/
# Should show: GeoLite2-Country.mmdb
```

---

## Phase 9: Configure Frontend Environment

### 9.1 Create Frontend .env.local

```bash
cd /home/admin/holding-cell/frontend

# Get the token from backend .env
TOKEN=$(grep WEBSOCKET_AUTH_TOKEN ../.env | cut -d'=' -f2)

# Create .env.local
cat > .env.local << EOF
# WebSocket connection URL
NEXT_PUBLIC_SOCKET_URL=wss://your-domain.com

# WebSocket authentication token (must match backend)
NEXT_PUBLIC_WEBSOCKET_AUTH_TOKEN=$TOKEN
EOF
```

---

## Phase 10: Update Nginx Production Config

### 10.1 Update Domain Placeholder

```bash
cd /home/admin/holding-cell

# Replace DOMAIN placeholder with your actual domain
sed -i "s/DOMAIN/your-domain.com/g" nginx/nginx.prod.conf

# Verify the change
grep ssl_certificate nginx/nginx.prod.conf
```

---

## Phase 11: Deploy with Docker Compose

### 11.1 Build and Start Services

```bash
cd /home/admin/holding-cell

# Build all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 11.2 Check Service Status

```bash
docker compose ps

# All services should show "running" or "healthy"
# Expected output:
# NAME                      STATUS
# holding-cell-backend-1    Up (healthy)
# holding-cell-frontend-1   Up
# holding-cell-nginx-1      Up
# holding-cell-cowrie-1     Up (healthy)
```

### 11.3 Check Logs

```bash
# Check all logs
docker compose logs -f

# Check specific service
docker compose logs backend
docker compose logs cowrie
docker compose logs nginx
```

---

## Phase 12: Verify Deployment

### 12.1 Test HTTPS Access

```bash
# On local machine
curl -I https://your-domain.com

# Should return 401 (needs auth) or 200 with basic auth
```

### 12.2 Test HTTP Basic Auth

```bash
# With auth
curl -u admin:your-password https://your-domain.com

# Should return HTML
```

### 12.3 Test WebSocket Connection

```javascript
// In browser console (authenticated on dashboard)
const token = 'your-websocket-token';
const socket = io('wss://your-domain.com', {
  transports: ['websocket'],
  auth: { token: token }
});

socket.on('connect', () => console.log('Connected!'));
socket.on('attack_event', (data) => console.log('Attack:', data));
```

### 12.4 Test Cowrie Honeypot

```bash
# From another machine, try to connect:
ssh -p 22 user@your-domain.com
# Should see Cowrie banner and get logged

telnet your-domain.com 23
# Should connect to Cowrie Telnet
```

### 12.5 Verify Non-Root Docker User

```bash
# Backend should run as appuser
docker compose exec backend whoami
# Should output: appuser
```

---

## Phase 13: Ongoing Maintenance

### 13.1 View Attack Logs

```bash
# Docker logs
docker compose logs -f cowrie

# Backend logs
docker compose logs -f backend

# Attack data persisted in volume
docker compose exec backend cat /data/attacks.json
```

### 13.2 Update Application

```bash
cd /home/admin/holding-cell

# Pull latest code
git pull

# Rebuild and restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 13.3 Backup Attack Data

```bash
# Create backup directory
mkdir -p backups

# Copy attack data from volume
docker compose cp backend:/data/attacks.json ./backups/attacks-$(date +%Y%m%d).json
```

### 13.4 Monitor Resources

```bash
# Check disk usage
df -h

# Check memory
free -h

# Check Docker resource usage
docker stats
```

---

## Troubleshooting

### Issue: Can't connect to WebSocket

```bash
# Check nginx logs
docker compose logs nginx

# Verify nginx is proxying correctly
docker compose exec nginx cat /etc/nginx/conf.d/default.conf | grep socket

# Check backend is running
docker compose logs backend | grep "Socket.IO"

# Verify auth token matches
grep WEBSOCKET_AUTH_TOKEN .env
grep NEXT_PUBLIC_WEBSOCKET_AUTH_TOKEN frontend/.env.local
```

### Issue: No attacks showing

```bash
# Check Cowrie is receiving connections
docker compose logs cowrie | grep "session"

# Check backend is reading logs
docker compose logs backend | grep "CowrieReader"

# Check GeoIP
ls -la geoip/GeoLite2-Country.mmdb
```

### Issue: SSL certificate errors

```bash
# Check certificate
sudo certbot certificates

# Renew if needed
sudo certbot renew --dry-run
```

### Issue: Auth rejected

```bash
# Verify tokens match
grep WEBSOCKET_AUTH_TOKEN .env
grep NEXT_PUBLIC_WEBSOCKET_AUTH_TOKEN frontend/.env.local

# Tokens must be identical
```

### Issue: Port 80 in use

```bash
# Stop nginx before certbot
docker compose stop nginx
sudo certbot renew --standalone
docker compose start nginx
```

---

## Security Checklist

- [ ] SSH on port 2244, root login disabled
- [ ] UFW firewall configured (only ports 2244, 22, 23, 80, 443)
- [ ] HTTP Basic Auth enabled on dashboard
- [ ] WebSocket authentication token configured
- [ ] SSL certificate installed and auto-renewing
- [ ] GeoIP database in place
- [ ] Docker backend runs as non-root user (`appuser`)
- [ ] Cowrie isolated on internal network
- [ ] htpasswd file permissions 640

---

## Architecture Summary

```
Internet
    │
    ├── Port 22/23 ──► Cowrie Honeypot (isolated network)
    │
    └── Port 443 ─────► Nginx
                            │
                            ├── / ──────────► Frontend (static files)
                            │
                            └── /socket.io/ ─► Backend (WebSocket)
                                    │
                                    └── Reads ──► Cowrie Logs (volume)
```

**Network Isolation:**
- Cowrie runs on `cowrie-network` with `internal: true` (no external internet)
- Backend reads logs via shared Docker volume (read-only)
- Frontend is static files served by nginx
- All WebSocket traffic goes through nginx

---

## Maintenance Commands Quick Reference

```bash
# View all logs
docker compose logs -f

# Restart services
docker compose restart

# Rebuild after updates
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Add new auth user
sudo htpasswd -B /etc/nginx/.htpasswd newuser
docker compose restart nginx

# Check service health
docker compose ps

# View attack history
docker compose exec backend cat /data/attacks.json | python -m json.tool
```