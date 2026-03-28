# VPS Deployment Guide

This guide covers deploying The Holding Cell to a VPS with HTTPS, authentication, and firewall security.

## Prerequisites

- Ubuntu 22.04+ VPS with root access
- Domain name with DNS A record pointing to VPS IP
- SSH access on alternate port (2244 recommended)

## Quick Start

1. Configure SSH on alternate port (2244)
2. Run UFW firewall setup
3. Install Docker and Docker Compose
4. Clone repository
5. Run Certbot to obtain SSL certificates
6. Create htpasswd file for authentication
7. Configure environment variables
8. Start services with Docker Compose
9. Enable certificate auto-renewal

## Detailed Steps

### 1. SSH Configuration (Port 2244)

Before configuring firewall, change SSH to alternate port:

```bash
# Edit SSH configuration
sudo nano /etc/ssh/sshd_config

# Change port to 2244
Port 2244

# Restart SSH
sudo systemctl restart sshd
```

Verify you can connect on port 2244 before continuing.

### 2. Firewall Setup

Run the UFW setup script:

```bash
chmod +x deploy/setup-ufw.sh
sudo ./deploy/setup-ufw.sh
```

This allows ports:
- 2244/tcp: Admin SSH
- 22/tcp: Cowrie SSH honeypot
- 23/tcp: Cowrie Telnet honeypot
- 80/tcp: HTTP (Let's Encrypt ACME)
- 443/tcp: HTTPS (dashboard)

### 3. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes
```

### 4. Clone Repository

```bash
# Clone to /opt/holding-cell
sudo mkdir -p /opt/holding-cell
sudo chown $USER:$USER /opt/holding-cell
git clone https://github.com/YOUR_REPO/holding-cell.git /opt/holding-cell
cd /opt/holding-cell
```

### 5. SSL Certificates

Obtain Let's Encrypt certificates using Certbot standalone mode:

```bash
# Install Certbot
sudo apt install certbot

# Stop nginx if running (to free port 80)
docker compose stop nginx 2>/dev/null || true

# Obtain certificate (replace your-domain.com)
sudo certbot certonly --standalone -d your-domain.com --email admin@your-domain.com --agree-tos --no-eff-email

# Certificates stored at:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 6. Authentication Setup

Create htpasswd file for HTTP Basic Auth:

```bash
chmod +x deploy/setup-htpasswd.sh
sudo ./deploy/setup-htpasswd.sh
```

Enter admin username and password when prompted.

### 7. Environment Configuration

Copy and edit .env file:

```bash
cp .env.example .env
nano .env
```

Required variables:
```
DOMAIN=your-domain.com
ADMIN_USER=admin
FRONTEND_PORT=80
HTTPS_PORT=443
COWRIE_SSH_PORT=2222
COWRIE_TELNET_PORT=2323
COWRIE_LOG_PATH=/var/log/cowrie
GEOIP_DB_PATH=/geoip/GeoLite2-Country.mmdb
```

### 8. Start Services

```bash
# Start with production override
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify all services running
docker compose ps

# Check logs
docker compose logs -f nginx
docker compose logs -f backend
```

### 9. Certificate Auto-Renewal

Install systemd timer for certificate renewal:

```bash
sudo cp deploy/certbot-renew.service /etc/systemd/system/
sudo cp deploy/certbot-renew.timer /etc/systemd/system/

# Update path in service file if needed
sudo sed -i "s|/opt/holding-cell|$(pwd)|g" /etc/systemd/system/certbot-renew.service

# Enable timer
sudo systemctl daemon-reload
sudo systemctl enable --now certbot-renew.timer

# Verify timer
sudo systemctl list-timers
```

### 10. Verify Deployment

Test the following:

1. **HTTPS Access**: `curl -I https://your-domain.com` (should return 401 Unauthorized)
2. **Authentication**: `curl -u admin:password https://your-domain.com` (should return 200)
3. **WebSocket**: Dashboard loads and shows "LIVE" badge
4. **Honeypot**: Port scans on 22/23 are logged by Cowrie

## Troubleshooting

### Port 80 in Use

If Certbot fails with "Port 80 is already in use":
```bash
docker compose stop nginx
sudo certbot renew --standalone
docker compose start nginx
```

### WebSocket Disconnects After 60 Seconds

Verify nginx.prod.conf has 24-hour timeouts:
```bash
grep "proxy_read_timeout" nginx/nginx.prod.conf
```
Should show `proxy_read_timeout 86400s`.

### Authentication Not Working

Check htpasswd file permissions:
```bash
ls -la /etc/nginx/.htpasswd
# Should be: -rw-r----- 1 root www-data
```

Regenerate if needed:
```bash
sudo ./deploy/setup-htpasswd.sh
docker compose restart nginx
```

### Certificate Renewal Failed

Check systemd logs:
```bash
sudo journalctl -u certbot-renew.service
```

## Network Architecture

```
Internet
    |
    |-- Port 22/tcp --> Cowrie SSH honeypot (isolated network)
    |-- Port 23/tcp --> Cowrie Telnet honeypot (isolated network)
    |-- Port 80/tcp --> nginx --> HTTP redirect to HTTPS
    |-- Port 443/tcp --> nginx --> FastAPI backend
    |                          |--> Static frontend files
    |
    |-- Port 2244/tcp --> SSH daemon (admin access)

Networks:
- app-network: nginx, frontend, backend
- cowrie-network: cowrie only (internal: true, no internet)

Data flow:
- Cowrie writes logs to /var/log/cowrie
- Backend reads logs via shared Docker volume (read-only)
- Backend emits attacks via Socket.io to frontend
- nginx terminates SSL, proxies WebSocket
```

## Security Checklist

- [ ] SSH on port 2244 (not default 22)
- [ ] UFW enabled with only required ports
- [ ] HTTPS with valid Let's Encrypt certificate
- [ ] HTTP Basic Auth configured
- [ ] htpasswd file permissions 640
- [ ] Certbot auto-renewal enabled
- [ ] Cowrie on isolated network
- [ ] Backend cannot reach Cowrie via network (only logs)
- [ ] No secrets in git repository

## Maintenance

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f cowrie
docker compose logs -f backend

# Systemd timer logs
sudo journalctl -u certbot-renew.timer
```

### Restart Services

```bash
# All services
docker compose restart

# Specific service
docker compose restart nginx
```

### Update Code

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Add New User

```bash
sudo htpasswd -B /etc/nginx/.htpasswd newuser
docker compose restart nginx
```