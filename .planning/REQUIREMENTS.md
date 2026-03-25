# Requirements: The Holding Cell

**Defined:** 2026-03-24
**Core Value:** A visually impressive, working real-time dashboard demonstrating SOC operations and threat intelligence skills through a distinctive arcade-meets-terminal aesthetic.

## v1 Requirements

### Backend Core

- [x] **BACK-01**: FastAPI server runs on port 8000 with async support
- [x] **BACK-02**: python-socketio AsyncServer handles WebSocket connections with `await sio.emit()` (not sync emit)
- [x] **BACK-03**: AttackGenerator produces fake attack events every 3-8 seconds (randomized)
- [x] **BACK-04**: FakeGenerator uses weighted archetype distribution (botnet_drone: 50%, script_kiddie: 30%, apt_operative: 10%, iot_worm: 7%, hacktivist: 3%)
- [x] **BACK-05**: AttackEvent includes: id, timestamp, ip, country, countryCode, port, protocol, archetype, commands, duration, rawLog
- [x] **BACK-06**: Fake IPs drawn from TEST-NET ranges (203.0.113.x, 198.51.100.x, 192.0.2.x)
- [x] **BACK-07**: Countries weighted toward realistic attacker origins (Russia, China, Brazil, Iran, etc.)
- [x] **BACK-08**: Archetype classifier assigns duration + commands based on fingerprint rules (script_kiddie <2min/<10cmds, apt_operative >10min/>50cmds with recon, etc.)
- [x] **BACK-09**: Socket emit failures logged with try/catch, no crash, no silent data loss

### Real-Time Connection

- [x] **RTCL-01**: Socket.io client connects to ws://localhost:8000 on page load
- [x] **RTCL-02**: Client auto-reconnects with exponential backoff (1s, 2s, 4s, max 30s) on disconnect
- [x] **RTCL-03**: "SIGNAL LOST" banner displayed on dashboard during disconnect
- [x] **RTCL-04**: Connection state displayed via "LIVE" badge with phosphor green glow pulse
- [x] **RTCL-05**: Events emitted during disconnect are lost (acceptable for Approach A v1)

### Jail Cell Visualization

- [x] **CELL-01**: JailCellGrid renders dark stone/brick CSS texture background
- [x] **CELL-02**: Iron bar SVG/CSS overlay covers the cell
- [x] **CELL-03**: Prisoners stack vertically from bottom, newest on top
- [x] **CELL-04**: Cell capacity: last 20 prisoners displayed
- [x] **CELL-05**: Prisoners older than 20 fade out gracefully (opacity transition)
- [x] **CELL-06**: Empty state: "The cell is empty. Waiting for attackers..." in pixel font style

### Prisoner Avatars

- [x] **PRSN-01**: 32x32 pixel-art PNG sprites per archetype (script_kiddie, botnet_drone, apt_operative, iot_worm, hacktivist)
- [x] **PRSN-02**: Sprites rendered at 64x64 with `image-rendering: pixelated`
- [x] **PRSN-03**: Each prisoner has distinct bandana color for visual variety
- [x] **PRSN-04**: Framer Motion spring entrance: `x: 800 → 0`, `type: "spring"`, `stiffness: 300, damping: 20`
- [x] **PRSN-05**: Prisoner lands at bottom of stack with small bounce
- [x] **PRSN-06**: Hover shows ArrestRecord tooltip (Framer Motion AnimatePresence)

### Arrest Record Tooltip

- [x] **TOOL-01**: Tooltip displays: IP address, country flag emoji, protocol/port, archetype badge, time "arrested"
- [x] **TOOL-02**: Retro terminal aesthetic: green text on black, monospace font, scanline overlay
- [x] **TOOL-03**: Positioned above avatar, centered

### Stats Panel

- [x] **STAT-01**: Displays: Total Attacks, Script Kiddies, APT Operatives, Botnet Drones, IoT Worms, Hacktivists
- [x] **STAT-02**: Retro LED counter aesthetic
- [x] **STAT-03**: Counters increment on each `attack_event` received
- [x] **STAT-04**: Numbers format with locale commas; cap display at 99,999+

### Frontend Stack

- [x] **FE-01**: Next.js 14 App Router, TypeScript, Tailwind CSS
- [x] **FE-02**: Framer Motion 11.x for animations
- [x] **FE-03**: Socket.io Client 4.x
- [x] **FE-04**: Design tokens from DESIGN.md (colors, typography, spacing)
- [x] **FE-05**: Dark mode primary, light mode toggle available
- [x] **FE-06**: IBM Plex Mono for IPs, timestamps, attack types (tabular-nums)

### Dev Experience

- [x] **DEV-01**: `npm run dev:backend` starts FastAPI on port 8000
- [x] **DEV-02**: `npm run dev:frontend` starts Next.js on port 3000
- [x] **DEV-03**: `npm run dev:all` runs both concurrently
- [x] **DEV-04**: backend/requirements.txt lists all Python dependencies
- [x] **DEV-05**: frontend/package.json lists all Node dependencies

## v2 Requirements

### Honeypot Integration

- **HONE-01**: Cowrie honeypot log tailer (Weekend 2)
- **HONE-02**: AttackSource abstraction interface for swappable data sources
- **HONE-03**: IP anonymization at backend boundary before data reaches frontend

### Enrichment

- **ENRH-01**: Shodan enrichment on prisoner hover (Weekend 3)
- **ENRH-02**: Per-IP cache with TTL for Shodan responses
- **ENRH-03**: Shodan Radar widget (fixed top-right, polling every 60s)

### Polish

- **POLY-01**: Demo speed mode (1-2s attack cadence)
- **POLY-02**: Persistent attacker identity across sessions
- **POLY-03**: Attack pattern indicator strip

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real Cowrie honeypot | Weekend 2 — validates concept with real data |
| VPS deployment | Weekend 2 — operational complexity beyond MVP |
| Full SIEM integration | Anti-feature — undermines portfolio demo purpose |
| AI/ML threat scoring | Anti-feature — adds complexity without visual value |
| World map visualization | Anti-feature — category convention, not this product's identity |
| Multi-honeypot aggregation | Anti-feature — single honeypot sufficient for portfolio |
| Docker/Ansible pipeline | Weekend 2+ — premature for MVP stage |
| PerthMiners disguise | Weekend 2 — SSH banner + fake commands |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BACK-01 | Phase 1 | Complete |
| BACK-02 | Phase 1 | Complete |
| BACK-03 | Phase 1 | Complete |
| BACK-04 | Phase 1 | Complete |
| BACK-05 | Phase 1 | Complete |
| BACK-06 | Phase 1 | Complete |
| BACK-07 | Phase 1 | Complete |
| BACK-08 | Phase 1 | Complete |
| BACK-09 | Phase 1 | Complete |
| RTCL-01 | Phase 1 | Complete |
| RTCL-02 | Phase 1 | Complete |
| RTCL-03 | Phase 1 | Complete |
| RTCL-04 | Phase 1 | Complete |
| RTCL-05 | Phase 1 | Complete |
| CELL-01 | Phase 2 | Complete |
| CELL-02 | Phase 2 | Complete |
| CELL-03 | Phase 2 | Complete |
| CELL-04 | Phase 2 | Complete |
| CELL-05 | Phase 2 | Complete |
| CELL-06 | Phase 2 | Complete |
| PRSN-01 | Phase 3 | Complete |
| PRSN-02 | Phase 3 | Complete |
| PRSN-03 | Phase 3 | Complete |
| PRSN-04 | Phase 3 | Complete |
| PRSN-05 | Phase 3 | Complete |
| PRSN-06 | Phase 3 | Complete |
| TOOL-01 | Phase 3 | Complete |
| TOOL-02 | Phase 3 | Complete |
| TOOL-03 | Phase 3 | Complete |
| STAT-01 | Phase 2 | Complete |
| STAT-02 | Phase 2 | Complete |
| STAT-03 | Phase 2 | Complete |
| STAT-04 | Phase 2 | Complete |
| FE-01 | Phase 1 | Complete |
| FE-02 | Phase 1 | Complete |
| FE-03 | Phase 1 | Complete |
| FE-04 | Phase 1 | Complete |
| FE-05 | Phase 1 | Complete |
| FE-06 | Phase 1 | Complete |
| DEV-01 | Phase 1 | Complete |
| DEV-02 | Phase 1 | Complete |
| DEV-03 | Phase 1 | Complete |
| DEV-04 | Phase 1 | Complete |
| DEV-05 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 38 total
- Mapped to phases: 38
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-24*
*Last updated: 2026-03-24 after roadmap creation*
