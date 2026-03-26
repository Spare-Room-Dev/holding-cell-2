# Phase 6: Cowrie Integration — Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Real SSH/Telnet attacks flow from Cowrie honeypot to frontend dashboard in real-time. This phase transforms the fake-data MVP into a live threat intelligence dashboard by connecting to the Cowrie honeypot configured in Phase 5. No persistence yet (Phase 7), no public deployment yet (Phase 8). The fake attack generator is disabled; all attacks shown are real.

</domain>

<decisions>
## Implementation Decisions

### Cowrie OT Persona
- **D-01:** Mining automation system persona — motd shows haul truck telemetry, filesystem has `/var/mining/`, usernames like `haulop`, `dispatch`, `supervisor`
- **D-02:** Use official `cowrie/cowrie:latest` image with volume-mounted config files (follows Phase 5 pattern)
- **D-03:** Configuration files: `motd` (mining system welcome), `fs` (filesystem layout with mining paths), `userdb.txt` (OT usernames)
- **D-04:** Cowrie SSH on port 2222, Telnet on port 2323 (per Phase 5 docker-compose.yml)

### Log Processing Architecture
- **D-05:** Async file tailing with Python watchdog or aiofiles — event-driven, low latency
- **D-06:** Backend reads `/var/log/cowrie/cowrie.json` via shared Docker volume (per Phase 5 D-03)
- **D-07:** New `cowrie_reader.py` module replaces `attack_generator.py` for real data
- **D-08:** Fake attack generator disabled entirely — dashboard shows only real attacks

### Session Correlation
- **D-09:** Emit attacks on session close only — complete data, accurate duration, all commands captured (per COW-03)
- **D-10:** Session ID from Cowrie logs groups events: connect, login, commands, close
- **D-11:** Duration calculated from session start to close timestamp

### Event Timing & Throttling
- **D-12:** Throttled emission (1-2 second buffer) to prevent UI flooding from rapid attacks
- **D-13:** Socket.io still uses same `attack_event` channel — frontend unchanged

### Archetype Classification
- **D-14:** Pure HASSH + command pattern matching (per COW-04)
- **D-15:** HASSH fingerprint extracted from Cowrie log field directly (Cowrie includes `hassh` in session events)
- **D-16:** HASSH-to-archetype mapping based on known SSH client fingerprints (Putty, OpenSSH, libssh, etc.)
- **D-17:** If HASSH unknown or missing (Telnet sessions): fall back to command pattern matching
- **D-18:** Command patterns from existing `ARCHETYPE_PROFILES`: `busybox/buildroot` → iot_worm, recon commands → apt_operative, etc.
- **D-19:** All 5 archetypes classified: script_kiddie, botnet_drone, apt_operative, iot_worm, hacktivist

### GeoIP Integration
- **D-20:** MaxMind GeoLite2 database (free, requires account signup)
- **D-21:** GeoIP database mounted as Docker volume to backend container
- **D-22:** Country code derived from attacker IP, mapped to country name via ISO 3166-1
- **D-23:** Country code used for flag emoji display in frontend (per COW-05)

### Claude's Discretion
- Exact watchdog/tailing implementation details
- HASSH fingerprint database source (use known fingerprints from Cowrie research)
- Exact throttle interval (recommend 1.5s as balance)
- GeoLite2 download automation (download once, mount as volume)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Decisions
- `PLAN.md` — Architecture diagram, data model, component specs
- `DESIGN.md` — Design tokens and aesthetic direction
- `.planning/PROJECT.md` — Tech stack, key decisions, aesthetic direction
- `.planning/REQUIREMENTS.md` — Phase 6 requirements: COW-01 to COW-05

### Prior Phases
- `.planning/phases/05-docker-containerization/05-CONTEXT.md` — Docker Compose structure, Cowrie on isolated network, volume sharing
- `.planning/phases/01-foundation/01-CONTEXT.md` — Backend architecture, Socket.io setup, AttackEvent model
- `.planning/phases/04-polish/04-CONTEXT.md` — Archetype classification rules per BACK-08

### Cowrie Documentation
- Cowrie honeypot documentation: https://cowrie.readthedocs.io/
- Cowrie JSON log format: https://cowrie.readthedocs.io/en/latest/jsonlogs.html
- HASSH fingerprinting: https://github.com/salesforce/hassh
- MaxMind GeoLite2: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

### Existing Code
- `backend/archetypes.py` — ARCHETYPE_PROFILES with fingerprint rules (adapt for real classification)
- `backend/models.py` — AttackEvent Pydantic model
- `backend/main.py` — FastAPI + Socket.io server (replace attack_emitter with cowrie_reader)

</canonical_refs>

<code_context>
## Existing Code Insights

### Backend Structure
- `backend/main.py` — FastAPI + Socket.io server with `attack_emitter()` background task (to be replaced)
- `backend/archetypes.py` — Classification rules designed for fake generation; patterns still valid for real attacks
- `backend/models.py` — AttackEvent Pydantic model with all required fields
- `backend/attack_generator.py` — Fake attack generator (to be replaced/disabled)
- `backend/requirements.txt` — Add `watchdog` or `aiofiles` for log tailing, `geoip2` for MaxMind

### Frontend Structure
- `frontend/src/lib/socket.ts` — Socket.io client, receives `attack_event` (unchanged)
- `frontend/src/types/attack.ts` — AttackEvent interface (unchanged)
- Frontend expects same AttackEvent schema — no changes needed

### Docker Compose
- `docker-compose.yml` — Cowrie already configured with log volume sharing
- Backend already mounts `cowrie-logs:/var/log/cowrie:ro`

### Integration Points
- New `cowrie_reader.py` module watches `/var/log/cowrie/cowrie.json`
- Session correlation logic groups events by `session` field
- Classification logic uses HASSH + commands to determine archetype
- GeoIP lookup uses MaxMind database for country data

</code_context>

<specifics>
## Specific Ideas

- Mining persona motd: "Welcome to HaulMax Fleet Management System v2.4.1\nSystem Status: OPERATIONAL\nLast Sync: [timestamp]"
- Mining filesystem: `/var/mining/logs/`, `/opt/caterpillar/`, `/home/operator/`
- Mining usernames: `haulop`, `dispatch`, `supervisor`, `mechanic`, `service`
- HASSH fingerprint mapping: Create a lookup dict mapping known HASSH hashes to client types
- Command pattern matching: Reuse ARCHETYPE_PROFILES patterns (busybox, recon, anonymous keywords)
- Throttle approach: Collect session-complete events in queue, emit to Socket.io every 1-2 seconds

</specifics>

<deferred>
## Deferred Ideas

- Attack persistence (last 20 attacks stored) — Phase 7
- Lifetime attack counter — Phase 7
- Top attacking locations analytics — Phase 7
- HTTPS/public deployment — Phase 8
- Authentication/authorization — Phase 8
- Multi-honeypot aggregation — Future

</deferred>

---

*Phase: 06-cowrie-integration*
*Context gathered: 2026-03-26*