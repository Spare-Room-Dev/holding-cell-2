---
phase: 08-vps-deployment-security
plan: 01
subsystem: infra
tags: [nginx, ssl, https, docker-compose, systemd, certbot, lets-encrypt]

# Dependency graph
requires:
  - phase: 05-docker-containerization
    provides: Docker Compose orchestration, nginx configuration, WebSocket timeouts
provides:
  - nginx.prod.conf with SSL termination and HTTPS redirect
  - docker-compose.prod.yml with SSL volume mounts
  - systemd timer for Let's Encrypt certificate renewal
affects: [phase-08-plan-02]

# Tech tracking
tech-stack:
  added: [certbot, systemd-timer]
  patterns: [ssl-termination, production-override, acme-challenge]

key-files:
  created:
    - nginx/nginx.prod.conf
    - docker-compose.prod.yml
    - deploy/certbot-renew.service
    - deploy/certbot-renew.timer
  modified: []

key-decisions:
  - "Certbot standalone mode for Let's Encrypt certificates (per D-05)"
  - "systemd timer runs twice daily at 00:00 and 12:00 (per D-06)"
  - "DOMAIN placeholder for certificate paths - replaced during deployment"
  - "24-hour WebSocket timeouts preserved from Phase 5 (per SEC-03)"

patterns-established:
  - "Pattern: Production Docker Compose override file for SSL mounts"
  - "Pattern: systemd timer with RandomizedDelaySec for certificate renewal"

requirements-completed: [SEC-02, SEC-03, SEC-05]

# Metrics
duration: 2min
completed: 2026-03-28
---
# Phase 08: VPS Deployment & Security - Plan 01 Summary

**nginx production configuration with HTTPS/SSL termination, Let's Encrypt certificate renewal via systemd timer, and Docker Compose production overrides for SSL volume mounts**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-28T09:01:41Z
- **Completed:** 2026-03-28T09:03:17Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- nginx.prod.conf with HTTP-to-HTTPS redirect and ACME challenge location
- HTTPS server block with modern TLS configuration (TLSv1.2/1.3)
- WebSocket proxy with 24-hour timeouts preserved from Phase 5
- docker-compose.prod.yml with SSL certificate volume mounts
- systemd timer for twice-daily certificate renewal

## Task Commits

Each task was committed atomically:

1. **Task 1: Create nginx.prod.conf with SSL termination and HTTPS redirect** - `0169203` (feat)
2. **Task 2: Create docker-compose.prod.yml with SSL volume mounts** - `4eb8b9a` (feat)
3. **Task 3: Create systemd timer for Let's Encrypt certificate renewal** - `7fbeb42` (feat)

## Files Created/Modified

- `nginx/nginx.prod.conf` - Production nginx config with SSL termination, HTTPS redirect, ACME challenge location, and WebSocket proxy
- `docker-compose.prod.yml` - Production override with SSL volume mounts (/etc/letsencrypt, /var/www/certbot)
- `deploy/certbot-renew.service` - systemd service that stops nginx, runs certbot renew, starts nginx
- `deploy/certbot-renew.timer` - systemd timer running twice daily at 00:00 and 12:00

## Decisions Made

- DOMAIN placeholder used for certificate paths - actual domain configured during VPS deployment
- Certbot standalone mode selected (per D-05) - requires stopping nginx during renewal
- systemd timer over cron for certificate renewal (per D-06) - better logging and persistent execution
- No authentication in this plan (htpasswd auth in Plan 08-02)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all configurations followed established patterns from RESEARCH.md.

## User Setup Required

**External services require manual configuration.** Domain DNS must point to VPS before certificates can be obtained:

1. Configure DNS A record pointing to VPS IP address
2. Run certbot standalone to obtain initial certificates
3. Copy systemd files to /etc/systemd/system/ and enable timer
4. Replace DOMAIN placeholder in nginx.prod.conf with actual domain

## Next Phase Readiness

- nginx.prod.conf ready for authentication layer (Plan 08-02)
- docker-compose.prod.yml ready for htpasswd volume mount (Plan 08-02)
- Certificate renewal automated via systemd timer

---

*Phase: 08-vps-deployment-security*
*Completed: 2026-03-28*

## Self-Check: PASSED
- nginx/nginx.prod.conf exists with listen 443 ssl
- docker-compose.prod.yml mounts /etc/letsencrypt
- deploy/certbot-renew.timer runs twice daily
- No hardcoded secrets in committed files
- Task commits 0169203, 4eb8b9a, 7fbeb42 verified