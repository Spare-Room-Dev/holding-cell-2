# Roadmap: The Holding Cell

## Overview

A gamified SOC/threat intelligence visualization dashboard that renders honeypot attacks as pixel-art "bandits" being thrown into a jail cell. Phase 1 establishes the real-time backend pipeline with fake attack data. Phase 2 delivers the static jail cell and stats visualization. Phase 3 adds the animated prisoner entrance experience. Phase 4 polishes and ships a recruiter-ready MVP.

## Phases

- [x] **Phase 1: Foundation** - Backend server, fake attack generator, Socket.io real-time pipeline, dev experience
- [ ] **Phase 2: Core Visualization** - JailCellGrid with stone texture + iron bars, StatsPanel with LED counters
- [ ] **Phase 3: Animated Prisoners** - Pixel-art sprites with spring entrance animation, ArrestRecord tooltip on hover
- [ ] **Phase 4: Polish** - Responsive layout, archetype classification end-to-end, demo-ready

## Phase Details

### Phase 1: Foundation
**Goal**: Backend server runs and emits fake attack events via Socket.io; frontend connects and displays connection status
**Depends on**: Nothing (first phase)
**Requirements**: BACK-01, BACK-02, BACK-03, BACK-04, BACK-05, BACK-06, BACK-07, BACK-08, BACK-09, RTCL-01, RTCL-02, RTCL-03, RTCL-04, RTCL-05, FE-01, FE-02, FE-03, FE-04, FE-05, FE-06, DEV-01, DEV-02, DEV-03, DEV-04, DEV-05
**Success Criteria** (what must be TRUE):
  1. Backend server starts on port 8000 with FastAPI + python-socketio async
  2. Fake attack events emit every 3-8 seconds via `await sio.emit()` with try/catch error handling
  3. AttackEvent includes id, timestamp, ip, country, countryCode, port, protocol, archetype, commands, duration, rawLog
  4. Socket.io client connects to ws://localhost:8000 on page load with auto-reconnect (1s, 2s, 4s, max 30s backoff)
  5. "SIGNAL LOST" banner displays during disconnect; "LIVE" badge shows phosphor green glow when connected
**Plans**: 4 plans in 3 waves

Plans:
- [x] 01-01-PLAN.md — Backend server + attack generator (BACK-01 to BACK-09, DEV-04)
- [x] 01-02-PLAN.md — Frontend scaffolding + design tokens (FE-01 to FE-06, DEV-05)
- [x] 01-03-PLAN.md — Socket.io client + Context + Connection UI (RTCL-01 to RTCL-05)
- [x] 01-04-PLAN.md — Root dev scripts + integration (DEV-01 to DEV-03)

### Phase 2: Core Visualization
**Goal**: JailCellGrid displays prisoners in a stone-textured cell with iron bars; StatsPanel shows attack counters
**Depends on**: Phase 1
**Requirements**: CELL-01, CELL-02, CELL-03, CELL-04, CELL-05, CELL-06, STAT-01, STAT-02, STAT-03, STAT-04
**Success Criteria** (what must be TRUE):
  1. JailCellGrid renders dark stone/brick CSS texture background with iron bar SVG overlay
  2. Prisoners stack vertically from bottom, newest on top, with 20-prisoner cap
  3. Prisoners older than 20 fade out gracefully (opacity transition)
  4. Empty state shows "The cell is empty. Waiting for attackers..." in pixel font style
  5. StatsPanel displays: Total Attacks, Script Kiddies, APT Operatives, Botnet Drones, IoT Worms, Hacktivists
  6. Counters increment on each attack_event received with retro LED aesthetic
**Plans**: 3 plans in 2 waves

Plans:
- [x] 02-01-PLAN.md — JailCellGrid with CSS textures + PrisonerSlot (CELL-01 to CELL-06)
- [x] 02-02-PLAN.md — StatsPanel with LED counters (STAT-01 to STAT-04)
- [ ] 02-03-PLAN.md — Dashboard integration with 70/30 sidebar layout

### Phase 3: Animated Prisoners
**Goal**: Prisoner avatars enter with Framer Motion spring physics; hover shows ArrestRecord tooltip
**Depends on**: Phase 2
**Requirements**: PRSN-01, PRSN-02, PRSN-03, PRSN-04, PRSN-05, PRSN-06, TOOL-01, TOOL-02, TOOL-03
**Success Criteria** (what must be TRUE):
  1. 32x32 pixel-art inline SVG sprites per archetype rendered at 56x56 with `image-rendering: pixelated`
  2. Each prisoner has distinct bandana color matching ARCHETYPE_COLORS mapping
  3. Framer Motion spring entrance: `y: -100 → 0` with `type: "spring"`, `stiffness: 300, damping: 20`, lands with small bounce
  4. Existing prisoners shift down with stiffer spring: `stiffness: 400, damping: 25`
  5. Hover shows ArrestRecord tooltip after 150ms delay: IP address, country flag emoji, protocol/port, archetype badge, commands count, duration, time arrested
  6. Tooltip styled as retro terminal: background #1A1A1A, phosphor border, IBM Plex Mono font
**Plans**: 2 plans in 2 waves

Plans:
- [ ] 03-01-PLAN.md — PrisonerSprite + ArrestRecordTooltip components (PRSN-01, PRSN-02, PRSN-03, TOOL-01, TOOL-02, TOOL-03)
- [ ] 03-02-PLAN.md — PrisonerSlot animation + JailCellGrid layout prop (PRSN-04, PRSN-05, PRSN-06)

### Phase 4: Polish
**Goal**: MVP ships with responsive layout, working archetype classification, and demo-ready experience
**Depends on**: Phase 3
**Requirements**: (All v1 requirements validated end-to-end)
**Success Criteria** (what must be TRUE):
  1. Dashboard responsive on desktop; no layout breaks at 1200px max-width
  2. All 5 archetype classifications work correctly based on fingerprint rules (script_kiddie <2min/<10cmds, botnet_drone repeated passwords, apt_operative >10min/>50cmds with recon, iot_worm buildroot/busybox/mips, hacktivist anonymous/free/hack in username)
  3. Dark mode primary active by default; light mode toggle functional
  4. Numbers format with locale commas; display caps at 99,999+
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2026-03-24 |
| 2. Core Visualization | 2/3 | In Progress|  |
| 3. Animated Prisoners | 0/2 | Not started | - |
| 4. Polish | 0/0 | Not started | - |

---

*Roadmap created: 2026-03-24*
*Granularity: coarse (4 phases)*
*Coverage: 38/38 v1 requirements mapped*
*Plans defined: 2026-03-24*
*Phase 2 plans created: 2026-03-25*
*Phase 3 plans created: 2026-03-25*