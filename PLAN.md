# Plan: The Holding Cell — Approach A (MVP with Fake Data)

Generated: 2026-03-24
Based on: design doc (rob-main-design-20260324-office-hours.md)
Approach: A — Fake Data + Socket.io + Next.js Dashboard

## Review History

- **2026-03-24** — plan-eng-review completed. Decisions below are FINAL.

---

## Overview

Approach A builds the full visual pipeline (Socket.io → Framer Motion → pixel-art prisoners) with simulated attack data. This validates the dashboard UX before introducing real honeypot complexity. Ships in Weekend 1.

**Goal:** A working, visually impressive dashboard that can demonstrate real-time attack visualization — with fake data that looks and feels real.

---

## Scope Decisions (Final)

| Decision | Change | Rationale |
|----------|--------|-----------|
| Remove Shodan radar | `RadarWidget` + `/shodan/:ip` endpoint removed | Not core to the app's value. Added in Weekend 3 if desired. |
| Absorb PrisonerStack into JailCellGrid | `PrisonerStack.tsx` deleted | Minimal diff: simpler = fewer abstractions |
| Socket event typing | `socket.ts` uses `AttackEvent` type | Explicit over clever — defensive coding |
| Socket failure handling | try/catch with retry on emit failures | Critical gap: silent data loss unacceptable |
| Realistic country weights | Use weighted real countries | More impressive for portfolio |
| Keep FastAPI + Socket.io | Not replaced with Next.js SSE | Weekend 2 Cowrie integration is Python-native — better to establish the stack now |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BROWSER (Next.js)                            │
│  ┌──────────────────┐        ┌─────────────────┐                   │
│  │  JailCellGrid   │        │   StatsPanel    │                   │
│  │  (pixel art +   │        │  (counters)     │                   │
│  │  Framer Motion) │        │                 │                   │
│  └────────┬─────────┘        └────────┬────────┘                  │
│           │                            │                           │
│           └────────────────────────────┼───────────────────────────┘
│                               socket.io                              │
│                               (client)                              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ ws://localhost:8000
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│                    PYTHON SERVER (FastAPI + Socket.io)               │
│  ┌──────────────────────┐    │    ┌──────────────────────────────┐   │
│  │  AttackGenerator    │─────┼───▶│  SocketServer (broadcast)  │   │
│  │  (fake data loop)  │    │    │                              │   │
│  └──────────────────────┘    │    └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, python-socketio (async), httpx, uvicorn
- Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion
- Ports: Backend on 8000, Frontend on 3000

---

## File Structure

```
holding-cell/
├── backend/
│   ├── main.py                    # FastAPI app + Socket.io server
│   ├── attack_generator.py         # Fake attack data generator
│   ├── models.py                  # Pydantic models (AttackEvent)
│   ├── archetypes.py               # Behavioral archetype classifier (reference rules only for Approach A)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Main dashboard
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   │
│   │   ├── components/
│   │   │   ├── JailCellGrid.tsx   # CSS Grid dungeon + prisoner stack (PrisonerStack absorbed)
│   │   │   ├── Prisoner.tsx       # Pixel-art avatar + tooltip
│   │   │   ├── StatsPanel.tsx     # Attack counters
│   │   │   └── ArrestRecord.tsx   # Tooltip content (IP, country, etc.)
│   │   │
│   │   ├── lib/
│   │   │   ├── socket.ts          # Socket.io client (typed with AttackEvent)
│   │   │   └── archetypes.ts      # Archetype type definitions
│   │   │
│   │   └── types/
│   │       └── attack.ts          # Shared AttackEvent type
│   │
│   ├── public/
│   │   └── sprites/                # Pixel art PNGs per archetype
│   │       ├── script-kiddie.png
│   │       ├── botnet-drone.png
│   │       ├── apt-operative.png
│   │       ├── iot-worm.png
│   │       └── hacktivist.png
│   │
│   ├── package.json
│   └── tailwind.config.ts
│
└── README.md
```

### Root Dev Scripts

```
# In root (or backend/Makefile):
dev:backend:
  cd backend && uvicorn main:app --reload --port 8000

dev:frontend:
  cd frontend && npm run dev

dev:all:   # runs both
  # Use concurrently: concurrently "npm run dev:backend" "npm run dev:frontend"
```

---

## Data Model

### AttackEvent (shared frontend/backend)

```typescript
interface AttackEvent {
  id: string;              // UUID
  timestamp: string;       // ISO 8601
  ip: string;             // "203.0.113.42"
  country: string;        // "Australia"
  countryCode: string;    // "AU"
  port: number;           // 22 (SSH)
  protocol: string;       // "SSH"
  archetype: Archetype;    // behavioral classification
  commands: string[];      // commands attempted
  duration: number;        // seconds
  rawLog: string;         // original fake log line
}

type Archetype =
  | "script_kiddie"
  | "botnet_drone"
  | "apt_operative"
  | "iot_worm"
  | "hacktivist";
```

### Fake Attack Generation Rules (archetypes.py logic)

Each archetype has distinct statistical fingerprints:

| Archetype | Duration | Commands | Key Indicators |
|-----------|----------|----------|----------------|
| script_kiddie | <2 min | <10 | no recon commands |
| botnet_drone | <5 min | <20 | repeated same passwords |
| apt_operative | >10 min | >50 | ls, pwd, cat /etc/passwd |
| iot_worm | any | any | buildroot/busybox/mips in probe |
| hacktivist | any | any | username contains anonymous/free/hack |

---

## API Contracts

### WebSocket: `attack_event` (server → client)

Server broadcasts on every new attack:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-24T10:30:00Z",
  "ip": "203.0.113.42",
  "country": "China",
  "countryCode": "CN",
  "port": 22,
  "protocol": "SSH",
  "archetype": "apt_operative",
  "commands": ["ls", "pwd", "cat /etc/passwd", "uname -a"],
  "duration": 847,
  "rawLog": "SSH attempt from 203.0.113.42: [invalid user root from 203.0.113.42 port 44521 ssh2]"
}
```

### REST: `GET /shodan/{ip}`

Queries Shodan for exposure status of a given IP.

**Request:** `GET /shodan/203.0.113.42`
**Response (exposed):**
```json
{
  "ip": "203.0.113.42",
  "status": "EXPOSED",
  "ports": [22, 80, 443],
  "vulns": ["CVE-2024-1234"],
  "lastUpdate": "2026-03-24T08:00:00Z"
}
```
**Response (stealth):**
```json
{
  "ip": "203.0.113.42",
  "status": "STEALTH",
  "ports": null,
  "vulns": null,
  "lastUpdate": null
}
```

**Error (Shodan rate limit):**
```json
{
  "error": "RATE_LIMITED",
  "message": "Shodan API quota exceeded"
}
```

---

## Component Specs

### `JailCellGrid` — The Dungeon Container

- **Style:** Dark grey stone texture (CSS background), iron bar overlay (CSS repeating-linear-gradient)
- **Layout:** CSS Grid, 1 column, auto-rows (avatars stack vertically from bottom)
- **Capacity:** Shows last 20 prisoners. Older ones fade out (opacity transition)
- **Empty state:** "The cell is empty. Waiting for attackers..." in pixel font

### `Prisoner` — Individual Avatar

- **Visual:** 32x32 PNG sprite per archetype, rendered at 64x64 with `image-rendering: pixelated`
- **Animation (Framer Motion):**
  - Enters from off-screen right (`x: 800 → 0`)
  - Physics: `type: "spring", stiffness: 300, damping: 20`
  - Lands at bottom of stack with a small bounce
- **Hover:** Shows `ArrestRecord` tooltip (Framer Motion `AnimatePresence`)

### `ArrestRecord` — Tooltip

- **Content:** IP address, country flag emoji, protocol/port, archetype badge, time "arrested"
- **Style:** Retro terminal aesthetic — green text on black, monospace font, scanline overlay
- **Position:** Above the avatar, centered

### `RadarWidget` — Shodan Status

- **Layout:** Top-right corner, fixed position
- **States:**
  - LOADING: Spinning radar animation
  - EXPOSED: Red border, "STATUS: EXPOSED" with port count
  - STEALTH: Green border, "STATUS: STEALTH"
  - ERROR: Grey border, "RADAR OFFLINE"
- **Polling:** Every 60 seconds (not 30 — avoids Shodan rate limit)

### `StatsPanel` — Attack Counters

- **Metrics:** Total Attacks, Script Kiddies, APT Operatives, Botnet Drones, IoT Worms, Hacktivists
- **Style:** Retro LED counter aesthetic
- **Updates:** Increments on each `attack_event` received

---

## Data Flow

### Fake Attack Generation Loop

```
attack_generator.py runs every 3-8 seconds (randomized interval):

1. Pick archetype weighted random (botnet_drone: 50%, script_kiddie: 30%,
   apt_operative: 10%, iot_worm: 7%, hacktivist: 3%)
2. Generate fake IP (from realistic IP ranges per country)
3. Generate fake commands list based on archetype rules
4. Create AttackEvent with timestamp + archetype fingerprint
5. Emit via socketio.emit('attack_event', event)
6. Log to server console with colored archetype tag
```

### Country/IP Generation

Fake IPs drawn from non-geographic dark ranges:
- 203.0.113.0/24 (TEST-NET-3)
- 198.51.100.0/24 (TEST-NET-2)
- 192.0.2.0/24 (TEST-NET-1)

Countries weighted toward known attacker origin countries:
Russia, China, Brazil, Iran, North Korea, Indonesia (adjustable weights).

---

## Error Handling

| Failure Mode | User Impact | Recovery |
|-------------|------------|----------|
| WebSocket disconnects | "SIGNAL LOST" banner on dashboard | Auto-reconnect with exponential backoff (1s, 2s, 4s, max 30s). Events emitted during disconnect are lost — acceptable for Approach A. |
| Socket emit failure | AttackGenerator logs error, skips event | try/catch around emit; no retry queue (would add complexity disproportionate to fake data value loss) |
| Too many prisoners | Cell caps at 20 | Oldest prisoner fades out gracefully |
| Invalid attack event | Drop event, log warning | Never crash the client on bad data |
| Stats counter overflow | Very large numbers | Format with locale commas; cap display at 99,999+ |

---

## Testing Plan

### Backend Tests

```
backend/
├── test_attack_generator.py
│   ├── test_archetype_weights_sum_to_one
│   ├── test_generates_valid_attack_event
│   ├── test_script_kiddie_duration_under_2min
│   ├── test_apt_operative_has_recon_commands
│   ├── test_botnet_drone_repeated_passwords
│   ├── test_iot_worm_banner_pattern
│   ├── test_hacktivist_username_pattern
│   └── test_socket_emit_failure_logs_error          # Critical gap fixed
│
└── test_socketio_integration.py
    └── test_emits_attack_event_on_interval
```

### Frontend Tests

```
frontend/
├── components/
│   ├── JailCellGrid.test.tsx
│   │   ├── test_renders_empty_state_when_no_prisoners
│   │   ├── test_caps_display_at_20_prisoners
│   │   └── test_oldest_prisoner_fades_out
│   │
│   ├── Prisoner.test.tsx
│   │   ├── test_renders_correct_sprite_for_archetype
│   │   ├── test_animation_plays_on_mount
│   │   ├── test_hover_shows_arrest_record
│   │   └── test_unknown_archetype_renders_fallback
│   │
│   └── StatsPanel.test.tsx
│       ├── test_increments_on_attack_event
│       └── test_counter_overflow_formats_correctly
│
└── lib/
    └── socket.test.ts
        ├── test_reconnects_with_backoff
        └── test_socket_events_typed_as_attack_event
```

### E2E Tests (Playwright)

```
e2e/
└── dashboard.spec.ts
    ├── test_see_prisoner_added_to_cell
    ├── test_hover_prisoner_shows_tooltip
    ├── test_stats_increment_on_attack
    └── test_reconnects_after_disconnect
```

---

## NOT in Scope

- **Real Cowrie honeypot integration** — deferred to Weekend 2
- **VPS deployment** — deferred to Weekend 2
- **PerthMiners disguise (SSH banner + fake commands)** — deferred to Weekend 2
- **Docker/Ansible deployment pipeline** — deferred to Weekend 2
- **Persistent attacker identity across sessions** — deferred
- **Deployment runbook for other students** — deferred
- **Actual malicious activity storage** — out of scope for MVP
- **Shodan radar widget** — removed per scope reduction decision
- **Demo speed mode** — not planned for Weekend 1 (3-8s cadence is fine for MVP)

## What Already Exists

Nothing. This is a greenfield project. The PRD and design doc define the WHAT; this plan defines the HOW.

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | — |
| Codex Review | `/codex review` | Independent 2nd opinion | 1 | issues_found | 13 findings; 1 critical (scope), 4 high, 4 medium, 1 strategic |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | clean | 4 issues found, all resolved; scope reduced (Shodan removed) |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |

**CODEX:** Dual-stack complexity (FastAPI vs SSE), boot orchestration missing, two sources of truth for archetypes, metrics semantics undefined, demo speed not planned
**CROSS-MODEL:** Review vs Codex agreed on: socket reliability concern (both flagged silent data loss risk), boot orchestration (both missed initially)
**UNRESOLVED:** 0
**VERDICT:** ENG CLEARED — ready to implement

## Open Questions (Resolved)

| Question | Resolution |
|----------|-----------|
| Shodan radar? | Removed. Not core value. Weekend 3 if desired. |
| VPS provider? | Deferred to Weekend 2. |
| Demo speed mode? | Not in Weekend 1 scope. Can add if cadence feels too slow. |
| Persistent attacker identity? | Deferred. Theme supported by session-only prisoner IDs. |
