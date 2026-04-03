# The Holding Cell

A gamified security operations center (SOC) visualization dashboard that renders honeypot attacks in real-time as pixel-art "bandits" being thrown into a jail cell.

![Holding Cell Dashboard](docs/screenshot.png)

## Overview

The Holding Cell connects to a Cowrie SSH/Telnet honeypot and visualizes incoming attacks in real-time. Each attacker is rendered as a pixel-art sprite with their country of origin, attack method, and timestamp. The dashboard provides an engaging way to monitor honeypot activity and gather threat intelligence.

### Key Features

- **Real-time attack visualization** - WebSocket-based live updates
- **Country identification** - GeoIP enrichment showing attacker origins
- **Attack history** - Persistent storage with crash recovery
- **Animated jail cell** - Pixel-art sprites with Framer Motion animations
- **Dark theme** - Security-focused aesthetic

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└─────────────┬───────────────────────────┬───────────────────────┘
              │                           │
              │ Port 22/23                │ Port 443
              ▼                           ▼
┌─────────────────────────┐     ┌─────────────────┐
│   Cowrie Honeypot       │     │      Nginx      │
│   (isolated network)    │     │   (SSL/Auth)    │
│                         │     │                 │
│   SSH:2222  Telnet:2323│     │  /       → static files
│         │               │     │  /socket → backend:8000
│         ▼               │     └────────┬────────┘
│   var/log/cowrie        │              │
└────────┬────────────────┘              ▼
         │                       ┌─────────────────┐
         │ Docker volume          │    Backend      │
         │ (read-only)           │   (FastAPI)     │
         ▼                       │                 │
┌─────────────────────────┐      │  - Socket.io    │
│   Backend reads logs     │◄─────┤  - GeoIP       │
│   GeoIP enrichment       │      │  - Persistence │
└─────────────────────────┘      └─────────────────┘
```

**Security:**
- Cowrie runs on an isolated internal network (no outbound internet)
- Backend reads logs via Docker volume (read-only mount)
- WebSocket authentication token required for connections
- HTTP Basic Auth protects the dashboard

## Quick Start

### Prerequisites

- Docker and Docker Compose
- MaxMind GeoLite2 Country database (free account required)

### Development

```bash
# Clone the repository
git clone <repo-url>
cd holding-cell

# Create geoip directory and add MaxMind database
mkdir -p geoip
# Place GeoLite2-Country.mmdb in geoip/

# Start services
docker compose up -d

# View logs
docker compose logs -f backend

# Dashboard available at http://localhost:3000
```

### GeoIP Setup

1. Create a free MaxMind account: https://www.maxmind.com/en/geolite2/signup
2. Download GeoLite2-Country.mmdb
3. Place at `geoip/GeoLite2-Country.mmdb`

**Fallback:** If the database is missing, the dashboard still works—all attacks show "Unknown" country.

## Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the complete Hetzner VPS deployment guide.

### Quick Production Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Generate WebSocket auth token
TOKEN=$(openssl rand -hex 32)
echo "WEBSOCKET_AUTH_TOKEN=$TOKEN" >> .env

# 3. Configure domain
sed -i "s/your-domain.com/your-actual-domain.com/g" nginx/nginx.prod.conf

# 4. Obtain SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# 5. Build and start
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRONTEND_PORT` | HTTP port for dashboard | `80` |
| `COWRIE_SSH_PORT` | External SSH honeypot port | `2222` |
| `COWRIE_TELNET_PORT` | External Telnet honeypot port | `2323` |
| `WEBSOCKET_AUTH_TOKEN` | Auth token for WebSocket connections | (required in production) |
| `DOMAIN` | Domain for SSL certificate | `your-domain.com` |

### Production Files

- `docker-compose.prod.yml` - Production overrides (SSL, auth)
- `nginx/nginx.prod.conf` - HTTPS config with Basic Auth
- `deploy/setup-ufw.sh` - Firewall configuration
- `deploy/setup-htpasswd.sh` - HTTP Basic Auth setup

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.11+, FastAPI, python-socketio, uvicorn |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| **Honeypot** | Cowrie SSH/Telnet honeypot |
| **Reverse Proxy** | Nginx (SSL termination, WebSocket proxy) |
| **Persistence** | JSON file-based attack history |
| **GeoIP** | MaxMind GeoLite2 Country database |

## Project Structure

```
holding-cell/
├── backend/           # FastAPI + Socket.io backend
│   ├── main.py        # Application entry point
│   ├── cowrie_reader.py   # Log file watcher
│   ├── geoip_service.py   # Country lookups
│   └── persistence.py     # Attack history storage
├── frontend/          # Next.js dashboard
│   ├── src/app/       # App Router pages
│   ├── src/components/    # React components
│   └── src/context/    # Socket context
├── nginx/              # Nginx configurations
│   ├── nginx.conf      # Development
│   └── nginx.prod.conf # Production (SSL, auth)
├── cowrie-config/      # Cowrie honeypot configs
│   ├── userdb.txt      # Fake user database
│   └── honeyfs/        # Fake filesystem
├── deploy/             # Deployment scripts
│   ├── setup-ufw.sh    # Firewall setup
│   └── setup-htpasswd.sh   # Auth setup
├── geoip/              # MaxMind database (gitignored)
├── docker-compose.yml  # Development config
├── docker-compose.prod.yml  # Production overrides
└── docs/DEPLOYMENT.md  # Full deployment guide
```

## Development

### Local Development (without Docker)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:combined_app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Environment Files

- `.env` - Backend environment (not committed)
- `frontend/.env.local` - Frontend environment (not committed)

Required frontend variables:
```bash
NEXT_PUBLIC_SOCKET_URL=ws://localhost:8000
NEXT_PUBLIC_WEBSOCKET_AUTH_TOKEN=your-token-here
```

## Troubleshooting

### WebSocket connection fails

```bash
# Check tokens match
grep WEBSOCKET_AUTH_TOKEN .env
grep NEXT_PUBLIC_WEBSOCKET_AUTH_TOKEN frontend/.env.local

# Check nginx proxy config
docker compose exec nginx cat /etc/nginx/conf.d/default.conf | grep socket
```

### No attacks appearing

```bash
# Check Cowrie is receiving connections
docker compose logs cowrie | grep session

# Check backend is processing logs
docker compose logs backend | grep CowrieReader

# Verify GeoIP database exists
ls -la geoip/GeoLite2-Country.mmdb
```

### SSL certificate issues

```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --standalone
```

## Security Notes

- **Cowrie is isolated** on an internal network with no internet access
- **Backend runs as non-root** (`appuser`) in Docker
- **Attack data is read-only** from the backend's perspective
- **WebSocket auth token** must match between frontend and backend
- **HTTP Basic Auth** protects the dashboard in production

> **⚠️ Honeypot Warning:** This project intentionally exposes SSH (port 22) and Telnet (port 23) to the internet to attract attackers. Only deploy on a dedicated VPS or isolated network. The honeypot will receive malicious traffic - ensure your hosting provider allows this use case.

## License

MIT

## Acknowledgments

- [Cowrie](https://github.com/cowrie/cowrie) - SSH/Telnet honeypot
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) - IP geolocation