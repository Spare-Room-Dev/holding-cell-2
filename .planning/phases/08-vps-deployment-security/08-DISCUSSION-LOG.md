# Phase 8: VPS Deployment & Security — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-28
**Phase:** 08-vps-deployment-security
**Areas discussed:** Authentication, HTTPS, Firewall, Deployment, Monitoring

---

## Authentication

| Option | Description | Selected |
|--------|-------------|----------|
| HTTP Basic Auth | Simple username/password in nginx. Works everywhere, no app changes. Easy to set up with htpasswd. | ✓ |
| IP Whitelist | Only allow specific IP addresses. No passwords to manage, but requires static IP or VPN. | |
| Both (IP whitelist + password fallback) | IP whitelist for known locations, password for access from anywhere else. Most secure but most complex. | |

**User's choice:** HTTP Basic Auth
**Notes:** Simple approach, no app changes needed, works with nginx htpasswd.

---

## HTTPS Certificate Management

| Option | Description | Selected |
|--------|-------------|----------|
| Certbot with standalone | Certbot obtains certificates before nginx starts. Requires temporary port 80 availability. Standard approach. | ✓ |
| Certbot with nginx plugin | Certbot configures nginx automatically. More integrated but requires nginx plugin installation. | |
| Caddy reverse proxy | Replace nginx with Caddy for automatic HTTPS. Simpler but requires learning Caddy and changing existing nginx config. | |

**User's choice:** Certbot with standalone
**Notes:** Standard Let's Encrypt approach, well-documented, works with existing nginx setup.

---

## Firewall Approach

| Option | Description | Selected |
|--------|-------------|----------|
| UFW (Uncomplicated Firewall) | Ubuntu's standard firewall. Simple commands, good defaults. Recommended for Ubuntu VPS. | ✓ |
| iptables directly | Raw iptables rules. More control but steeper learning curve. No abstraction layer. | |
| Cloud provider firewall | Use DigitalOcean/AWS/Vultr firewall rules instead of host-level. Requires provider console access. | |

**User's choice:** UFW (Uncomplicated Firewall)
**Notes:** Simple, standard for Ubuntu, good defaults.

---

## Admin SSH Port

| Option | Description | Selected |
|--------|-------------|----------|
| Port 2222 (Recommended) | Non-standard port reduces automated attacks. Already used for Cowrie honeypot SSH on 2222 externally. | ✓ |
| Port 22 (standard) | Standard SSH port. Simpler but higher attack exposure. | |
| Custom port (e.g., 2244) | Choose a different non-standard port. Avoids conflict with Cowrie's external port. | |

**User's choice:** Port 2222
**Notes:** Decision updated to 2244 in CONTEXT.md to avoid conflict with Cowrie honeypot port mapping.

---

## Domain

| Option | Description | Selected |
|--------|-------------|----------|
| I have a domain ready | I have a domain ready to point to this VPS. I'll configure DNS myself. | ✓ |
| Use IP only for now | I'll use the VPS IP address directly for testing, add domain later. | |
| Decide domain later | I'll set up the domain after getting the VPS deployed. | |

**User's choice:** Have domain ready
**Notes:** User will configure DNS to point to VPS.

---

## Deployment Process

| Option | Description | Selected |
|--------|-------------|----------|
| Manual (SSH + git pull) (Recommended) | SSH into VPS, git pull, docker compose up. Simple and transparent. | ✓ |
| GitHub Actions CI/CD | Push to main triggers deployment via GitHub Actions. More automation, requires secrets setup. | |
| Webhook-based auto-deploy | Watch GitHub repo for changes and auto-pull. Middle ground between manual and CI/CD. | |

**User's choice:** Manual (SSH + git pull)
**Notes:** Simple manual process suitable for portfolio demo.

---

## Secrets Storage

| Option | Description | Selected |
|--------|-------------|----------|
| .env file on server (Recommended) | Store passwords in .env file on VPS (gitignored). Simple, works with HTTP Basic Auth. | ✓ |
| Docker secrets or Vault | Use Docker Swarm secrets or HashiCorp Vault. More secure but adds complexity. | |

**User's choice:** .env file on server
**Notes:** Pattern already established from Phase 5. Secrets in gitignored .env file.

---

## Monitoring

| Option | Description | Selected |
|--------|-------------|----------|
| Log viewing only (Recommended) | Use 'docker compose logs' and 'journalctl' for debugging. No additional services. Simple. | ✓ |
| Add Dozzle log viewer | Docker container for log aggregation with web UI. More visibility but another service to maintain. | |
| Prometheus + Grafana | Full monitoring stack. Most visibility, most complexity. Overkill for portfolio. | |

**User's choice:** Log viewing only
**Notes:** Keep it simple for portfolio demo, no additional monitoring infrastructure.

---

## Certificate Renewal

| Option | Description | Selected |
|--------|-------------|----------|
| Certbot systemd timer (Recommended) | Set up cron/systemd timer for 'certbot renew'. Standard approach for Let's Encrypt. | ✓ |
| Certbot Docker with built-in renewal | Let certbot's built-in renewal timer handle it. Simpler but relies on Docker. | |

**User's choice:** Certbot systemd timer
**Notes:** Standard approach, runs twice daily to check for renewal.

---

## Honeypot Port Exposure

| Option | Description | Selected |
|--------|-------------|----------|
| Public (all IPs) (Recommended) | Honeypot ports 22 and 23 accept connections from anywhere. Maximum attack visibility. | ✓ |
| Restrict to specific ranges | Only allow honeypot connections from specific networks. Reduces noise but may miss attacks. | |

**User's choice:** Public (all IPs)
**Notes:** Maximum attack visibility for portfolio demo.

---

## HTTP Traffic Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Redirect HTTP to HTTPS (Recommended) | Redirect all HTTP to HTTPS. Standard security practice. | ✓ |
| Allow both HTTP and HTTPS | Allow HTTP access without redirect. Only for testing, not recommended for production. | |

**User's choice:** Redirect HTTP to HTTPS
**Notes:** Standard security practice, no unencrypted access.

---

## Claude's Discretion

Areas where user said "you decide" or deferred to implementation:
- Exact htpasswd file location and permissions
- Exact UFW rules syntax and order
- Exact systemd timer unit file for certbot renewal
- Exact nginx SSL configuration for HTTPS
- Docker Compose production override file structure

## Deferred Ideas

- Multi-user authentication system — Future
- OAuth/SSO integration — Future
- Backup/restore automation — Future
- Monitoring dashboards (Grafana) — Future
- Log aggregation (Dozzle, Loki) — Future
- Rate limiting — Future
- Fail2ban for brute force protection — Future