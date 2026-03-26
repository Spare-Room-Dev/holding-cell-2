# The Holding Cell

A gamified SOC/threat intelligence visualization dashboard that renders honeypot attacks as pixel-art "bandits" being thrown into a jail cell.

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

The dashboard will be available at http://localhost:3000

## GeoIP Setup (Required for Country Lookups)

The Holding Cell uses MaxMind GeoLite2 for IP-to-country enrichment.

### Setup Steps

1. Create a free MaxMind account at https://www.maxmind.com/en/geolite2/signup
2. Download GeoLite2-Country.mmdb from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
3. Create the geoip directory and place the database:

   ```bash
   mkdir -p geoip
   # Place downloaded file as:
   # geoip/GeoLite2-Country.mmdb
   ```

4. The database is mounted to the backend container via docker-compose.yml

### Fallback Behavior

If the GeoLite2 database is not found:
- All attacker IPs will show "Unknown" country
- A warning is logged on backend startup
- The dashboard continues to function without country data

### Docker Compose Volume Mount

The docker-compose.yml includes:
```yaml
backend:
  volumes:
    - ./geoip:/geoip:ro
  environment:
    - GEOIP_DB_PATH=/geoip/GeoLite2-Country.mmdb
```

## Development

See `DESIGN.md` for design tokens and aesthetic direction.
See `PLAN.md` for architecture and implementation details.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, python-socketio, uvicorn
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion
- **Honeypot:** Cowrie SSH/Telnet honeypot