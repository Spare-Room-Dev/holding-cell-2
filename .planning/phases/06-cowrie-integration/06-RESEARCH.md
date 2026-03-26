# Phase 6: Cowrie Integration - Research

**Researched:** 2026-03-26
**Domain:** Cowrie honeypot integration, real-time log processing, HASSH fingerprinting, GeoIP enrichment
**Confidence:** HIGH

## Summary

This phase integrates real SSH/Telnet attack data from Cowrie honeypot into the Holding Cell dashboard. The implementation requires: (1) configuring Cowrie with an OT/mining persona, (2) implementing async file tailing to watch Cowrie's JSON logs, (3) correlating session events by session ID, (4) classifying attacks using HASSH fingerprints and command patterns, and (5) enriching attacker IPs with GeoIP country data.

**Primary recommendation:** Use `watchfiles` for async log monitoring (native async support), `geoip2` library with MaxMind GeoLite2-Country.mmdb for IP enrichment, and emit complete session data only on `cowrie.session.closed` events for accurate duration/command counts.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Cowrie OT Persona
- **D-01:** Mining automation system persona — motd shows haul truck telemetry, filesystem has `/var/mining/`, usernames like `haulop`, `dispatch`, `supervisor`
- **D-02:** Use official `cowrie/cowrie:latest` image with volume-mounted config files
- **D-03:** Configuration files: `motd` (mining system welcome), `fs` (filesystem layout), `userdb.txt` (OT usernames)
- **D-04:** Cowrie SSH on port 2222, Telnet on port 2323

#### Log Processing Architecture
- **D-05:** Async file tailing with Python watchdog or aiofiles — event-driven, low latency
- **D-06:** Backend reads `/var/log/cowrie/cowrie.json` via shared Docker volume
- **D-07:** New `cowrie_reader.py` module replaces `attack_generator.py` for real data
- **D-08:** Fake attack generator disabled entirely — dashboard shows only real attacks

#### Session Correlation
- **D-09:** Emit attacks on session close only — complete data, accurate duration, all commands captured
- **D-10:** Session ID from Cowrie logs groups events: connect, login, commands, close
- **D-11:** Duration calculated from session start to close timestamp

#### Event Timing & Throttling
- **D-12:** Throttled emission (1-2 second buffer) to prevent UI flooding
- **D-13:** Socket.io still uses same `attack_event` channel — frontend unchanged

#### Archetype Classification
- **D-14:** Pure HASSH + command pattern matching
- **D-15:** HASSH fingerprint extracted from Cowrie log field directly
- **D-16:** HASSH-to-archetype mapping based on known SSH client fingerprints
- **D-17:** If HASSH unknown or missing (Telnet sessions): fall back to command pattern matching
- **D-18:** Command patterns from existing `ARCHETYPE_PROFILES`: `busybox/buildroot` → iot_worm, recon commands → apt_operative, etc.
- **D-19:** All 5 archetypes classified: script_kiddie, botnet_drone, apt_operative, iot_worm, hacktivist

#### GeoIP Integration
- **D-20:** MaxMind GeoLite2 database (free, requires account signup)
- **D-21:** GeoIP database mounted as Docker volume to backend container
- **D-22:** Country code derived from attacker IP, mapped to country name via ISO 3166-1
- **D-23:** Country code used for flag emoji display in frontend

### Claude's Discretion
- Exact watchdog/tailing implementation details
- HASSH fingerprint database source (use known fingerprints from Cowrie research)
- Exact throttle interval (recommend 1.5s as balance)
- GeoLite2 download automation (download once, mount as volume)

### Deferred Ideas (OUT OF SCOPE)
- Attack persistence (last 20 attacks stored) — Phase 7
- Lifetime attack counter — Phase 7
- Top attacking locations analytics — Phase 7
- HTTPS/public deployment — Phase 8
- Authentication/authorization — Phase 8
- Multi-honeypot aggregation — Future
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COW-01 | Cowrie honeypot configured as mining/industrial site persona | Section: Cowrie OT Persona Configuration |
| COW-02 | Attack data flows from Cowrie JSON logs to backend via Socket.io in real-time | Section: Log Processing Architecture |
| COW-03 | Session correlation groups related events by session ID | Section: Session Correlation Logic |
| COW-04 | All 5 archetypes classified from real attack fingerprints | Section: Archetype Classification |
| COW-05 | GeoIP country data derived from attacker IP addresses | Section: GeoIP Integration |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `watchfiles` | 1.1.1 | Async file watching for Cowrie JSON logs | Native async support, Rust-based performance, actively maintained |
| `geoip2` | 5.2.0 | MaxMind GeoLite2 country lookups | Official MaxMind Python library, simple API |
| `python-socketio` | 5.11.0+ | WebSocket real-time communication | Already in project, proven working |
| `FastAPI` | 0.135.0+ | Async web framework | Already in project, proven working |

### Supporting

| Library | Purpose | When to Use |
|---------|---------|-------------|
| `aiofiles` | Async file I/O | Alternative to watchfiles for simpler use cases |
| `asyncio` | Async task orchestration | Built-in, used for background task management |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `watchfiles` | `watchdog` | watchdog lacks native async support, requires workarounds |
| `watchfiles` | `async-tail` | async-tail is newer, less battle-tested than watchfiles |
| `geoip2.database` | `maxminddb` (raw) | geoip2 provides nicer API with country names included |

**Installation:**
```bash
pip install watchfiles>=1.1.1 geoip2>=5.2.0
```

**Version verification:**
- `watchfiles`: 1.1.1 (2024-11, actively maintained)
- `geoip2`: 5.2.0 (official MaxMind library)

## Architecture Patterns

### Recommended Project Structure

```
backend/
├── main.py                 # FastAPI + Socket.io server (modified)
├── cowrie_reader.py        # NEW: Async log watcher + session correlation
├── archetypes.py           # Classification rules (updated for real data)
├── geoip_service.py        # NEW: MaxMind GeoIP lookup service
├── models.py               # AttackEvent Pydantic model (unchanged)
├── attack_generator.py     # DISABLED: Fake generator (remove from main.py)
└── requirements.txt        # Add: watchfiles, geoip2

cowrie-config/              # NEW: Volume-mounted Cowrie configuration
├── userdb.txt              # OT usernames for honeypot
├── motd                    # Mining system welcome banner
└── honeyfs/                # Custom filesystem content
    └── etc/
        └── motd            # Post-login banner

geoip/                      # NEW: MaxMind database directory
└── GeoLite2-Country.mmdb   # Downloaded manually, mounted as volume
```

### Pattern 1: Async File Watching with watchfiles

**What:** Use `watchfiles.awatch()` to monitor Cowrie JSON logs in real-time without blocking the event loop.

**When to use:** Primary pattern for log tailing in Phase 6.

**Example:**
```python
# Source: watchfiles documentation + best practices
import asyncio
from watchfiles import awatch
import json

async def watch_cowrie_logs(log_path: str):
    """Watch Cowrie JSON log for new entries."""
    async for changes in awatch(log_path):
        for change_type, path in changes:
            if change_type == Change.added or change_type == Change.modified:
                # Read new lines from the file
                async with aiofiles.open(path, 'r') as f:
                    async for line in f:
                        try:
                            event = json.loads(line.strip())
                            await process_cowrie_event(event)
                        except json.JSONDecodeError:
                            continue
```

### Pattern 2: Session Correlation

**What:** Buffer events by session ID, emit complete AttackEvent on `cowrie.session.closed`.

**When to use:** Required for accurate duration and command counts (per D-09).

**Example:**
```python
# In-memory session buffer
sessions: dict[str, dict] = {}

async def process_cowrie_event(event: dict):
    """Correlate events by session ID."""
    session_id = event.get("session")
    event_type = event.get("eventid")

    if event_type == "cowrie.session.connect":
        # New session - initialize
        sessions[session_id] = {
            "src_ip": event.get("src_ip"),
            "src_port": event.get("src_port"),
            "timestamp": event.get("timestamp"),
            "commands": [],
            "hassh": None,
            "username": None,
        }

    elif event_type == "cowrie.client.kex":
        # SSH key exchange - extract HASSH fingerprint
        if session_id in sessions:
            sessions[session_id]["hassh"] = event.get("hassh")

    elif event_type == "cowrie.login.success":
        # Successful login
        if session_id in sessions:
            sessions[session_id]["username"] = event.get("username")

    elif event_type == "cowrie.command.input":
        # Command executed
        if session_id in sessions:
            sessions[session_id]["commands"].append(event.get("input"))

    elif event_type == "cowrie.session.closed":
        # Session complete - emit AttackEvent
        if session_id in sessions:
            session_data = sessions.pop(session_id)
            session_data["duration"] = event.get("duration", 0)
            await emit_attack_event(session_id, session_data)
```

### Pattern 3: HASSH Fingerprint Classification

**What:** Map known HASSH fingerprints to SSH client types, fall back to command patterns for unknown.

**When to use:** Primary classification method for SSH attacks (per D-14, D-15).

**Example:**
```python
# Known HASSH fingerprints (from salesforce/hassh GitHub)
KNOWN_HASSH = {
    # Script kiddie tools
    "b5752e36ba6c5979a575e43178908adf": "script_kiddie",  # Python Paramiko (Metasploit)
    "fafc45381bfde997b6305c4e1600f1bf": "script_kiddie",  # Ruby/Net::SSH (Metasploit)

    # Botnet drones
    "de30354b88bae4c2810426614e1b6976": "botnet_drone",   # PowerShell Renci.SshNet (Empire)

    # IoT worms
    "16f898dd8ed8279e1055350b4e20666c": "iot_worm",       # Dropbear 2012.55 (embedded)

    # APT operatives (OpenSSH variants)
    "06046964c022c6407d15a27b12a6a4fb": "apt_operative",  # OpenSSH 7.7p1
}

def classify_by_hassh(hassh: str | None) -> Archetype | None:
    """Classify by HASSH fingerprint if known."""
    if hassh and hassh in KNOWN_HASSH:
        return KNOWN_HASSH[hassh]
    return None

def classify_by_commands(commands: list[str]) -> Archetype:
    """Fall back to command pattern classification."""
    command_str = " ".join(commands).lower()

    # IoT worm signatures
    if "busybox" in command_str or "buildroot" in command_str:
        return "iot_worm"

    # APT signatures (extensive recon)
    recon_patterns = ["netstat", "ps aux", "cat /etc/shadow", "find / -name"]
    if sum(1 for p in recon_patterns if p in command_str) >= 2:
        return "apt_operative"

    # Hacktivist signatures
    hacktivist_keywords = ["anonymous", "free", "hack", "anon", "hacker"]
    if any(kw in command_str for kw in hacktivist_keywords):
        return "hacktivist"

    # Botnet drone (credential stuffing)
    if "login attempt:" in command_str:
        return "botnet_drone"

    # Default: script kiddie
    return "script_kiddie"
```

### Pattern 4: GeoIP Lookup

**What:** Use geoip2 library with GeoLite2-Country.mmdb for IP-to-country enrichment.

**When to use:** Required for COW-05 (country display in dashboard).

**Example:**
```python
# Source: geoip2 documentation
import geoip2.database
from functools import lru_cache

class GeoIPService:
    def __init__(self, db_path: str = "/geoip/GeoLite2-Country.mmdb"):
        self.reader = geoip2.database.Reader(db_path)

    def get_country(self, ip: str) -> tuple[str, str]:
        """
        Get country name and code for an IP address.

        Returns:
            tuple: (country_name, country_code) or ("Unknown", "XX")
        """
        try:
            response = self.reader.country(ip)
            return (
                response.country.name or "Unknown",
                response.country.iso_code or "XX"
            )
        except Exception:
            return ("Unknown", "XX")

    def close(self):
        self.reader.close()

# Usage (singleton pattern in FastAPI app state)
geoip_service = GeoIPService("/geoip/GeoLite2-Country.mmdb")
country_name, country_code = geoip_service.get_country("192.0.2.1")
```

### Anti-Patterns to Avoid

- **Blocking the event loop:** Never use synchronous file I/O inside async functions. Use `watchfiles.awatch()` or `aiofiles.open()`.
- **Emitting on every log line:** Emit only on `cowrie.session.closed` to ensure complete data (duration, commands).
- **GeoIP lookups in hot path without caching:** Session-based correlation provides natural batching, but consider caching for repeated IPs.
- **Hardcoding HASSH fingerprints:** Store in a config file for easy updates as new signatures are discovered.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File watching | Custom polling loop | `watchfiles.awatch()` | Native async, handles file rotation, handles log rotation |
| Country lookup | HTTP API calls | `geoip2.database.Reader` | Local MMDB is faster, no rate limits, works offline |
| HASSH fingerprinting | Custom hash computation | Cowrie's built-in `hassh` field | Cowrie already extracts HASSH from SSH handshake |
| Session correlation | Per-event emission | Buffer + emit on close | Accurate duration and command counts |

**Key insight:** Cowrie already does the heavy lifting (HASSH extraction, session tracking). The integration layer only needs to watch, correlate, and classify.

## Runtime State Inventory

> This phase does not involve rename/refactor/migration. No runtime state inventory required.

## Common Pitfalls

### Pitfall 1: Missing Session Events Due to Log Rotation

**What goes wrong:** Cowrie rotates log files, causing the file watcher to lose track of the active file.

**Why it happens:** `watchfiles` watches the file descriptor, not the path. When Cowrie rotates, new entries go to a new file.

**How to avoid:** Watch the directory, not the file. Use `awatch(directory_path)` to catch both modifications to existing file and creation of new log files.

**Warning signs:** Attacks stop appearing in dashboard after log rotation time (usually midnight).

### Pitfall 2: GeoIP Database Not Mounted in Docker

**What goes wrong:** Backend fails to start or returns "Unknown" for all countries because GeoLite2 database is missing.

**Why it happens:** The GeoLite2 database must be downloaded separately (requires MaxMind account) and mounted as a volume.

**How to avoid:**
1. Document the download step clearly
2. Add startup check that validates GeoLite2-Country.mmdb exists
3. Provide clear error message if missing

**Warning signs:** Backend logs "GeoIP database not found" on startup, all attacks show "Unknown" country.

### Pitfall 3: HASSH Missing for Telnet Sessions

**What goes wrong:** Telnet sessions have no HASSH fingerprint because HASSH is SSH-specific.

**Why it happens:** HASSH relies on SSH key exchange algorithm negotiation, which Telnet doesn't have.

**How to avoid:** Always fall back to command pattern classification when HASSH is missing or unknown. The `classify_by_commands()` function handles this case.

**Warning signs:** Telnet attacks all classified as "script_kiddie" regardless of behavior.

### Pitfall 4: Session Memory Leak

**What goes wrong:** Sessions dictionary grows indefinitely if `cowrie.session.closed` events are missed.

**Why it happens:** Network issues or log gaps can cause missing close events.

**How to avoid:** Implement a TTL-based cleanup that removes sessions older than 24 hours, or emit incomplete sessions after a timeout.

**Warning signs:** Backend memory usage grows over time, never decreases.

## Code Examples

Verified patterns from official sources:

### Cowrie JSON Event Structure

```json
// Source: https://docs.cowrie.org/en/latest/OUTPUT.html

// Session connect
{
  "eventid": "cowrie.session.connect",
  "timestamp": "2024-01-15T14:30:00.123456Z",
  "session": "a1b2c3d4e5f6",
  "src_ip": "192.168.1.100",
  "src_port": 54321,
  "dst_ip": "10.0.0.1",
  "dst_port": 2222
}

// SSH key exchange (contains HASSH)
{
  "eventid": "cowrie.client.kex",
  "timestamp": "2024-01-15T14:30:01.234567Z",
  "session": "a1b2c3d4e5f6",
  "src_ip": "192.168.1.100",
  "hassh": "b5752e36ba6c5979a575e43178908adf",
  "hasshAlgorithms": "curve25519-sha256,...",
  "kexAlgs": ["curve25519-sha256", "..."],
  "keyAlgs": ["ssh-rsa", "..."]
}

// Successful login
{
  "eventid": "cowrie.login.success",
  "timestamp": "2024-01-15T14:30:05.345678Z",
  "session": "a1b2c3d4e5f6",
  "src_ip": "192.168.1.100",
  "username": "root",
  "password": "admin123"
}

// Command input
{
  "eventid": "cowrie.command.input",
  "timestamp": "2024-01-15T14:30:10.456789Z",
  "session": "a1b2c3d4e5f6",
  "src_ip": "192.168.1.100",
  "input": "cat /etc/passwd"
}

// Session closed
{
  "eventid": "cowrie.session.closed",
  "timestamp": "2024-01-15T14:32:45.567890Z",
  "session": "a1b2c3d4e5f6",
  "src_ip": "192.168.1.100",
  "duration": 125.47
}
```

### Docker Compose Volume Mounts for Cowrie Config

```yaml
# Source: https://github.com/cowrie/cowrie Docker documentation
services:
  backend:
    volumes:
      - cowrie-logs:/var/log/cowrie:ro
      - ./geoip:/geoip:ro  # GeoLite2 database

  cowrie:
    image: cowrie/cowrie:latest
    volumes:
      - cowrie-logs:/cowrie/cowrie-git/var/log/cowrie
      - ./cowrie-config/userdb.txt:/cowrie/cowrie-git/etc/userdb.txt:ro
      - ./cowrie-config/honeyfs:/cowrie/cowrie-git/honeyfs:ro
```

### Cowrie Configuration Files

```ini
# etc/cowrie.cfg - Basic configuration
[honeypot]
hostname = haulmax-fleet-01

[ssh]
enabled = true
listen_endpoints = tcp:2222:interface=0.0.0.0

[telnet]
enabled = true
listen_endpoints = tcp:2223:interface=0.0.0.0
```

```text
# etc/userdb.txt - OT usernames for mining persona
# Format: username:uid:password
# * = wildcard password (accepts anything)
# ! = deny this password

root:x:!root
root:x:!123456
root:x:!password
root:x:*
haulop:x:*
dispatch:x:*
supervisor:x:*
mechanic:x:*
service:x:*
operator:x:*
admin:x:*
```

```text
# honeyfs/etc/motd - Mining system welcome banner
Welcome to HaulMax Fleet Management System v2.4.1
System Status: OPERATIONAL
Last Sync: 2026-03-26T08:30:00Z

Active Units: 12 haul trucks, 3 loaders
Current Shift: Day Operations

Type 'help' for available commands.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Polling log files | watchfiles/async file watching | 2020+ | Native async, no blocking |
| HTTP GeoIP API calls | Local MMDB database | Standard practice | No rate limits, works offline |
| Per-event emission | Session correlation + emit on close | Per D-09 | Accurate duration and command counts |

**Deprecated/outdated:**
- `watchdog` without async wrapper: Use `watchfiles` instead for native async support
- Synchronous file reading in async context: Always use `aiofiles` or `watchfiles`

## Open Questions

1. **Throttle Interval Optimization**
   - What we know: CONTEXT.md suggests 1-2 seconds
   - What's unclear: Exact optimal value for UI smoothness vs. attack burst handling
   - Recommendation: Start with 1.5 seconds, measure during testing

2. **GeoLite2 Download Automation**
   - What we know: Requires MaxMind account, manual download
   - What's unclear: Whether to automate via GeoIP Update tool or document manual step
   - Recommendation: Document manual download in README, add startup validation check

3. **HASSH Fingerprint Database Updates**
   - What we know: Salesforce HASSH repo is archived (read-only)
   - What's unclear: Best source for ongoing fingerprint updates
   - Recommendation: Create local `hassh_signatures.json` config file for easy manual updates

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3.11+ | Backend runtime | ✓ | — | — |
| Docker | Cowrie container | ✓ | — | — |
| docker-compose | Service orchestration | ✓ | — | — |
| MaxMind GeoLite2 | Country lookup | Manual | — | Return "Unknown" for all IPs if missing |
| Cowrie image | Honeypot | ✓ | cowrie/cowrie:latest | — |

**Missing dependencies with no fallback:**
- None (all core dependencies available)

**Missing dependencies with fallback:**
- MaxMind GeoLite2 database: Not installed by default, requires manual download. Fallback: return "Unknown" country with warning log.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing project structure) |
| Config file | None (uses pytest auto-discovery) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v --cov=backend` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| COW-01 | Cowrie OT persona configured | integration | `pytest tests/test_cowrie_config.py -v` | Wave 0 |
| COW-02 | Real attacks flow via Socket.io | integration | `pytest tests/test_cowrie_reader.py::test_session_flow -v` | Wave 0 |
| COW-03 | Session correlation groups events | unit | `pytest tests/test_cowrie_reader.py::test_session_correlation -v` | Wave 0 |
| COW-04 | All 5 archetypes classified | unit | `pytest tests/test_archetypes.py::test_hassh_classification -v` | Wave 0 |
| COW-05 | GeoIP country lookup | unit | `pytest tests/test_geoip.py -v` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v --cov=backend`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_cowrie_reader.py` — covers COW-02, COW-03 (session correlation, log watching)
- [ ] `tests/test_archetypes.py::test_hassh_classification` — covers COW-04 (HASSH mapping)
- [ ] `tests/test_geoip.py` — covers COW-05 (country lookup)
- [ ] `tests/test_cowrie_config.py` — covers COW-01 (OT persona validation)
- [ ] `tests/conftest.py` — shared fixtures (sample Cowrie events, mock GeoIP reader)

## Sources

### Primary (HIGH confidence)

- [Cowrie JSON Log Format](https://docs.cowrie.org/en/latest/OUTPUT.html) — Event types and field structure
- [HASSH GitHub Repository](https://github.com/salesforce/hassh) — Known fingerprints, MD5 calculation method
- [geoip2 Python Documentation](https://geoip2.readthedocs.io/en/stable/) — Official MaxMind Python library API
- [MaxMind GeoLite2 Developer Portal](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data/) — Download requirements, EULA
- [watchfiles PyPI](https://pypi.org/project/watchfiles/) — Native async file watching library

### Secondary (MEDIUM confidence)

- [Cowrie Docker Documentation](https://docs.cowrie.org/en/stable/docker/README.html) — Volume mounting patterns
- [Cowrie userdb.example](https://github.com/cowrie/cowrie/blob/main/etc/userdb.example) — Credential format
- [Docker Hub cowrie/cowrie](https://hub.docker.com/r/cowrie/cowrie) — Image usage and configuration
- [SANS ISC Cowrie Analysis](https://isc.sans.edu/diary/29714) — Real-world JSON log examples with HASSH

### Tertiary (LOW confidence)

- [async-tail PyPI](https://pypi.org/project/async-tail/) — Alternative async tailing (less mature than watchfiles)
- [aiowatcher GitHub](https://github.com/py-paulo/aiowatcher) — Alternative async watcher library

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — watchfiles and geoip2 are mature, well-documented libraries
- Architecture: HIGH — patterns follow official documentation and established async practices
- Pitfalls: HIGH — based on documented Cowrie behavior and common Docker volume issues

**Research date:** 2026-03-26
**Valid until:** 90 days (Cowrie and libraries are stable)