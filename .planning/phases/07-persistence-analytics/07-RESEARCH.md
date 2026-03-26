# Phase 7: Persistence & Analytics — Research

**Researched:** 2026-03-26
**Domain:** Python/JSON persistence, Socket.io history delivery, React state aggregation
**Confidence:** HIGH

## Summary

This phase adds persistence and analytics to the existing real-time attack pipeline. The implementation is straightforward: JSON file for persistence (same Docker volume pattern as Cowrie logs), Socket.io history event for new connections, in-memory aggregations updated incrementally on each attack, and extended StatsPanel UI for analytics display. No new external dependencies required — uses existing patterns from the codebase.

**Primary recommendation:** Use Python's built-in `json` module with atomic write pattern (write to temp file, then rename) for persistence. Extend SocketContext to receive `attack_history` event and update aggregations incrementally. Reuse existing CounterBox component for lifetime counter, create minimal new components for country list and methods panel.

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

### Persistence Storage
- **D-01:** JSON file for attack history — simple, Docker volume-friendly, easy to inspect
- **D-02:** `attacks.json` stored in shared Docker volume (same pattern as Cowrie logs)
- **D-03:** Persist every attack immediately after emission — no data loss on crash
- **D-04:** Last 20 attacks stored as array, newest first, capped at 20 items

### State Sharing & Connection
- **D-05:** New visitors receive history on socket connect via `attack_history` event
- **D-06:** Server maintains in-memory copy of last 20 attacks for fast history delivery
- **D-07:** On server startup, load history from JSON file into memory
- **D-08:** After each attack: emit to all clients, append to memory, flush to JSON file

### Lifetime Attack Counter
- **D-09:** Cumulative counter stored in same JSON file as attack history
- **D-10:** Counter starts at 0 on first deployment, increments forever
- **D-11:** No reset functionality — counter reflects total attacks since deployment
- **D-12:** Counter persisted immediately with each attack (same write as history)

### Top Analytics (STAT-02, STAT-03)
- **D-13:** Top 5 attacking countries displayed by attack count
- **D-14:** Protocol breakdown: SSH vs Telnet counts
- **D-15:** Port breakdown: Top 5 most-targeted ports
- **D-16:** Real-time incremental aggregation — update counts on each attack
- **D-17:** Aggregations stored in memory and persisted with history JSON
- **D-18:** Recompute aggregations on startup from attack history (fallback)

### UI Layout
- **D-19:** Extend existing StatsPanel component with new sections
- **D-20:** New sections below archetype counters: "Lifetime Attacks", "Top Countries", "Attack Methods"
- **D-21:** LED counter aesthetic maintained (consistent with existing StatsPanel)
- **D-22:** No new panel components — keep single unified stats display

### Claude's Discretion
- Exact JSON file structure (recommend: `{attacks: [], lifetime_count: N, analytics: {...}}`)
- Exact aggregation schema (recommend: `{countries: {US: N, ...}, protocols: {SSH: N, TELNET: N}, ports: {22: N, ...}}`)
- Exact placement of new sections within StatsPanel (recommend: after archetype counters, before scrollable area)
- Error handling for corrupted JSON file (recommend: start fresh, log warning)

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| STORE-01 | Last 20 attacks stored persistently (survives server restart) | JSON file with atomic write pattern; see Architecture Patterns |
| STORE-02 | All visitors see the same attack history (shared state) | Server-side in-memory cache + `attack_history` event on connect |
| STORE-03 | New visitors see existing attacks immediately on connect | Socket.io `connect` handler emits history; see Socket.io Patterns |
| STAT-01 | Lifetime attack counter shows total attacks since deployment | Cumulative counter in JSON file, increments on each attack |
| STAT-02 | Top attacking locations displayed (countries by attack count) | Incremental aggregation in memory, countries dict from countryCode field |
| STAT-03 | Top attack methods displayed (SSH vs Telnet, ports targeted) | Incremental aggregation: protocols dict (SSH/TELNET), ports dict |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| json | stdlib | JSON file persistence | Python built-in, atomic write pattern with temp file + os.replace |
| os | stdlib | File operations | Python built-in for atomic file writes |
| python-socketio | 5.9.0+ | History event emission | Already in use for attack_event, same pattern for attack_history |

### Frontend

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React Context | 18+ | State management for aggregations | Already in use (SocketContext), extend with analytics state |
| Framer Motion | 11.x | Animation for new sections | Already in use, same CounterBox pulse animation |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| asyncio.Lock | stdlib | Thread-safe file writes | Wrap JSON write operations for async safety |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| JSON file | SQLite | SQLite adds complexity, JSON is simpler and Docker-volume-friendly per D-01 |
| JSON file | Redis | Overkill for 20-item history, adds deployment dependency |
| In-memory aggregations | Recompute on every request | Incremental update is O(1) per attack vs O(n) recompute |

---

## Architecture Patterns

### Recommended JSON File Structure

```json
{
  "attacks": [
    {
      "id": "uuid",
      "timestamp": "2026-03-26T10:30:00Z",
      "ip": "192.0.2.1",
      "country": "China",
      "countryCode": "CN",
      "port": 22,
      "protocol": "SSH",
      "archetype": "apt_operative",
      "commands": ["ls", "cat /etc/passwd"],
      "duration": 847,
      "rawLog": "[SSH] Session abc123 from 192.0.2.1..."
    }
    // ... up to 20 items, newest first
  ],
  "lifetime_count": 1247,
  "analytics": {
    "countries": {
      "CN": 247,
      "RU": 183,
      "BR": 92,
      "US": 45,
      "IR": 38
    },
    "protocols": {
      "SSH": 892,
      "TELNET": 355
    },
    "ports": {
      "22": 892,
      "23": 355
    }
  }
}
```

### Backend Persistence Pattern

```python
# backend/persistence.py (new module)
import json
import os
import asyncio
from pathlib import Path
from typing import Optional

# Atomic write pattern for crash safety
PERSISTENCE_FILE = Path("/data/attacks.json")
TEMP_FILE = Path("/data/attacks.json.tmp")

class PersistenceManager:
    """Manages attack history and analytics persistence."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self.attacks: list[dict] = []
        self.lifetime_count: int = 0
        self.analytics: dict = {
            "countries": {},
            "protocols": {},
            "ports": {}
        }

    async def load(self) -> None:
        """Load history from JSON file on startup."""
        async with self._lock:
            if PERSISTENCE_FILE.exists():
                try:
                    with open(PERSISTENCE_FILE, 'r') as f:
                        data = json.load(f)
                    self.attacks = data.get("attacks", [])
                    self.lifetime_count = data.get("lifetime_count", 0)
                    self.analytics = data.get("analytics", {
                        "countries": {}, "protocols": {}, "ports": {}
                    })
                    print(f"[Persistence] Loaded {len(self.attacks)} attacks, count={self.lifetime_count}")
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"[Persistence] Corrupted file, starting fresh: {e}")
                    self._reset()
            else:
                print("[Persistence] No history file, starting fresh")
                self._reset()

    def _reset(self) -> None:
        """Reset to empty state."""
        self.attacks = []
        self.lifetime_count = 0
        self.analytics = {"countries": {}, "protocols": {}, "ports": {}}

    async def add_attack(self, attack: dict) -> None:
        """Add attack, update aggregations, persist atomically."""
        async with self._lock:
            # Increment lifetime counter
            self.lifetime_count += 1

            # Add to history (newest first, cap at 20)
            self.attacks.insert(0, attack)
            if len(self.attacks) > 20:
                self.attacks = self.attacks[:20]

            # Update aggregations incrementally
            country_code = attack.get("countryCode", "XX")
            self.analytics["countries"][country_code] = \
                self.analytics["countries"].get(country_code, 0) + 1

            protocol = attack.get("protocol", "SSH")
            self.analytics["protocols"][protocol] = \
                self.analytics["protocols"].get(protocol, 0) + 1

            port = str(attack.get("port", 22))
            self.analytics["ports"][port] = \
                self.analytics["ports"].get(port, 0) + 1

            # Atomic write: write to temp, then replace
            await self._flush()

    async def _flush(self) -> None:
        """Write to JSON file atomically."""
        data = {
            "attacks": self.attacks,
            "lifetime_count": self.lifetime_count,
            "analytics": self.analytics
        }
        # Write to temp file first
        with open(TEMP_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        # Atomic replace
        os.replace(TEMP_FILE, PERSISTENCE_FILE)

    def get_history(self) -> list[dict]:
        """Return last 20 attacks for history event."""
        return self.attacks

    def get_analytics(self) -> dict:
        """Return current analytics snapshot."""
        return self.analytics

    def get_lifetime_count(self) -> int:
        """Return cumulative attack count."""
        return self.lifetime_count
```

**Source:** Python stdlib patterns for atomic file writes (os.replace is atomic on POSIX)

### Socket.io History Event Pattern

```python
# In main.py, add to connect handler

@sio.event
async def connect(sid: str, environ: dict, auth: dict) -> None:
    """Handle client connection - send history on connect."""
    print(f"[Socket.IO] Client connected: {sid}")

    # Per D-05: New visitors receive history on connect
    # Per D-06: Server maintains in-memory copy for fast delivery
    history = persistence_manager.get_history()
    analytics = persistence_manager.get_analytics()
    lifetime = persistence_manager.get_lifetime_count()

    await sio.emit('attack_history', {
        'attacks': history,
        'lifetime_count': lifetime,
        'analytics': analytics
    }, to=sid)
```

**Source:** Existing Socket.io patterns from main.py (connect handler, attack_event emission)

### Frontend State Management Pattern

```typescript
// frontend/src/context/SocketContext.tsx (extend existing)

interface SocketState {
  status: ConnectionStatus;
  attacks: AttackEvent[];
  // New fields for Phase 7
  lifetimeCount: number;
  analytics: {
    countries: Record<string, number>;
    protocols: Record<string, number>;
    ports: Record<string, number>;
  };
}

type SocketAction =
  | { type: 'CONNECTED' }
  | { type: 'DISCONNECTED' }
  | { type: 'RECONNECTING' }
  | { type: 'NEW_ATTACK'; payload: AttackEvent }
  | { type: 'ATTACK_HISTORY'; payload: { attacks: AttackEvent[]; lifetime_count: number; analytics: Analytics } };

function socketReducer(state: SocketState, action: SocketAction): SocketState {
  switch (action.type) {
    case 'ATTACK_HISTORY':
      // Replace entire state with history from server
      return {
        ...state,
        status: 'connected',
        attacks: action.payload.attacks,
        lifetimeCount: action.payload.lifetime_count,
        analytics: action.payload.analytics,
      };
    case 'NEW_ATTACK':
      // Incremental update: prepend attack, increment counters
      const newAnalytics = { ...state.analytics };
      const attack = action.payload;

      // Update country count
      newAnalytics.countries[attack.countryCode] =
        (newAnalytics.countries[attack.countryCode] || 0) + 1;

      // Update protocol count
      newAnalytics.protocols[attack.protocol] =
        (newAnalytics.protocols[attack.protocol] || 0) + 1;

      // Update port count
      const portStr = String(attack.port);
      newAnalytics.ports[portStr] =
        (newAnalytics.ports[portStr] || 0) + 1;

      return {
        ...state,
        attacks: [attack, ...state.attacks].slice(0, 100),
        lifetimeCount: state.lifetimeCount + 1,
        analytics: newAnalytics,
      };
    // ... other cases unchanged
  }
}

// In SocketProvider useEffect:
socket.on('attack_history', (data: AttackHistoryPayload) => {
  console.log('[Socket] Received attack history:', data.attacks.length, 'attacks');
  dispatch({ type: 'ATTACK_HISTORY', payload: data });
});
```

**Source:** Existing SocketContext.tsx patterns (reducer, NEW_ATTACK action)

### StatsPanel Extension Pattern

```tsx
// frontend/src/components/StatsPanel.tsx (extend existing)

// Add new imports
import { useMemo } from 'react';
import { CounterBox } from './CounterBox';
import { CountryList } from './CountryList';
import { MethodsPanel } from './MethodsPanel';

export function StatsPanel() {
  const { state } = useSocket();

  // Derive top 5 countries from analytics
  const topCountries = useMemo(() => {
    const entries = Object.entries(state.analytics.countries);
    return entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);
  }, [state.analytics.countries]);

  // Derive top 5 ports from analytics
  const topPorts = useMemo(() => {
    const entries = Object.entries(state.analytics.ports);
    return entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);
  }, [state.analytics.ports]);

  return (
    <div className="flex flex-col gap-md">
      {/* Row 1: Archetype counters (existing) */}
      <div className="flex flex-row gap-md flex-wrap">
        <CounterBox label="Total" value={counts.total} />
        {/* ... existing archetype counters */}
      </div>

      {/* Row 2: Analytics row (new, per D-19, D-20) */}
      <div className="flex flex-row gap-md flex-wrap">
        <CounterBox label="Lifetime" value={state.lifetimeCount} />
        <CountryList countries={topCountries} />
        <MethodsPanel
          protocols={state.analytics.protocols}
          ports={topPorts}
        />
      </div>
    </div>
  );
}
```

**Source:** Existing StatsPanel.tsx structure, UI-SPEC.md layout specifications

### Country Flag Emoji Mapping

```typescript
// frontend/src/utils/countryToFlag.ts

/**
 * Convert ISO 3166-1 alpha-2 country code to flag emoji.
 *
 * Algorithm: Each character in the code is offset by 0x1F3E0 to get
 * the regional indicator symbol. Two letters form the flag emoji.
 *
 * Example: "CN" -> 🇨🇳
 */
export function countryCodeToFlag(code: string): string {
  if (!code || code.length !== 2) return '🏳️'; // Fallback
  const base = 0x1F1E6; // Regional indicator A
  const char1 = String.fromCodePoint(base + (code.charCodeAt(0) - 65));
  const char2 = String.fromCodePoint(base + (code.charCodeAt(1) - 65));
  return char1 + char2;
}
```

**Source:** Unicode regional indicator symbols (standard emoji flag encoding)

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Country name from code | Custom mapping | ISO 3166-1 lookup or flag emoji | Standardized, no maintenance |
| JSON persistence | Custom format | JSON file with atomic write | Simple, debuggable, Docker-volume-friendly |
| State management | Redux/MobX | React Context + useReducer (existing) | Already in use, no new dependencies |
| Counter animation | Custom animation | Existing CounterBox component | Consistent LED aesthetic, Framer Motion |

**Key insight:** Extend existing patterns rather than introducing new abstractions. The SocketContext and StatsPanel already have established patterns — follow them.

---

## Runtime State Inventory

> This phase involves persistence but no rename/refactor operations. Skipping runtime state inventory.

---

## Common Pitfalls

### Pitfall 1: JSON File Corruption on Crash
**What goes wrong:** Writing directly to JSON file can leave partial/corrupted file if server crashes mid-write.
**Why it happens:** Python's `open(f, 'w')` truncates first; crash leaves empty file.
**How to avoid:** Use atomic write pattern: write to temp file, then `os.replace()` (atomic on POSIX).
**Warning signs:** Empty attacks.json after server crash, `json.JSONDecodeError` on startup.

### Pitfall 2: Race Condition Between History and New Attack
**What goes wrong:** Client receives history event and then a new attack event, but history didn't include the attack.
**Why it happens:** History is sent on connect, but attacks continue arriving during transmission.
**How to avoid:** This is expected behavior per D-08. History gives snapshot at connect time; new attacks arrive via attack_event. No race condition — events are ordered per Socket.io session.
**Warning signs:** If client sees duplicate attacks, check that attack IDs are unique.

### Pitfall 3: Aggregation Drift from History Mismatch
**What goes wrong:** Aggregations computed from history don't match lifetime_count after restart.
**Why it happens:** History is capped at 20 attacks, but lifetime_count is cumulative.
**How to avoid:** Aggregations and lifetime_count are independent. Aggregations show recent patterns (last 20 attacks), lifetime shows total since deployment. Per D-18, recompute aggregations from history on startup only as fallback — normal operation uses incremental updates.
**Warning signs:** Aggregations don't sum to lifetime_count — this is expected, not a bug.

### Pitfall 4: Country Flag Emoji Rendering
**What goes wrong:** Flag emojis show as two letters or empty boxes on some systems.
**Why it happens:** Not all platforms support regional indicator symbols (older Windows, some Linux).
**How to avoid:** Provide fallback (🏳️ white flag) when conversion fails. Test on target platforms.
**Warning signs:** Country flags render incorrectly on Windows.

### Pitfall 5: Port Number as Object Key
**What goes wrong:** Port stored as number in analytics.ports but accessed as string in frontend.
**Why it happens:** JSON keys are always strings; JavaScript object keys are coerced to strings.
**How to avoid:** Store ports as strings in analytics dict: `str(attack.get("port", 22))`. Document this in code comments.

---

## Code Examples

### Backend: Persistence Integration in main.py

```python
# backend/main.py (modifications)

from persistence import PersistenceManager

# Initialize persistence manager
persistence_manager = PersistenceManager()

@app.on_event('startup')
async def startup() -> None:
    """Start server with persistence."""
    # Load history from JSON file
    await persistence_manager.load()

    # Start Cowrie watcher
    asyncio.create_task(cowrie_emitter())
    print("[FastAPI] Server started, persistence loaded, Cowrie watcher running")

@sio.event
async def connect(sid: str, environ: dict, auth: dict) -> None:
    """Handle client connection - send history on connect."""
    print(f"[Socket.IO] Client connected: {sid}")

    # Per D-05: Send history on connect
    await sio.emit('attack_history', {
        'attacks': persistence_manager.get_history(),
        'lifetime_count': persistence_manager.get_lifetime_count(),
        'analytics': persistence_manager.get_analytics()
    }, to=sid)

# In cowrie_emitter(), after attack emission:
async def emit_attack(attack_dict: dict) -> None:
    try:
        await sio.emit('attack_event', attack_dict)
        # Per D-03: Persist immediately after emission
        await persistence_manager.add_attack(attack_dict)
    except Exception as e:
        print(f"[CowrieEmitter] Failed to emit/persist attack: {e}")
```

### Frontend: CountryList Component

```tsx
// frontend/src/components/CountryList.tsx
'use client';

import { countryCodeToFlag } from '@/utils/countryToFlag';
import type { Archetype } from '@/types/attack';

interface CountryListProps {
  countries: [string, number][]; // [countryCode, count] pairs
}

export function CountryList({ countries }: CountryListProps) {
  if (countries.length === 0) {
    return (
      <div className="flex flex-col items-center gap-xs">
        <span className="counter-label">Top Countries</span>
        <span className="text-text-muted text-sm">No attacks yet</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-xs">
      <span className="counter-label">Top Countries</span>
      <div className="flex flex-col gap-2xs">
        {countries.map(([code, count]) => (
          <div
            key={code}
            className="flex items-center gap-xs text-sm font-mono"
          >
            <span>{countryCodeToFlag(code)}</span>
            <span className="text-text-muted">
              {getCountryName(code)}
            </span>
            <span className="text-primary font-mono">
              {count.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Country code to name lookup (ISO 3166-1)
const COUNTRY_NAMES: Record<string, string> = {
  CN: 'China',
  RU: 'Russia',
  US: 'United States',
  BR: 'Brazil',
  IR: 'Iran',
  // ... add more as needed
};

function getCountryName(code: string): string {
  return COUNTRY_NAMES[code] || code;
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Redis for session state | In-memory + JSON file | D-01, D-02 | Simpler deployment, Docker-volume-friendly |
| Recompute aggregations on every request | Incremental updates | D-16 | O(1) per attack vs O(n) per request |
| Client-side history management | Server-sent history on connect | D-05 | Consistent state for all visitors |

**Deprecated/outdated:**
- LocalStorage for history: Not shared across visitors, defeats STORE-02
- SQLite for 20-item history: Overkill complexity, JSON is simpler

---

## Open Questions

1. **JSON file location on host**
   - What we know: Docker volume `cowrie-logs` exists at `/var/log/cowrie` in container. Backend mounts it read-only.
   - What's unclear: Should `attacks.json` go in a new volume or same volume as Cowrie logs?
   - Recommendation: Use new volume `persistence-data` mapped to `/data` in container. Keeps persistence separate from Cowrie logs, follows Docker volume best practices.

2. **Country name mapping completeness**
   - What we know: GeoIP service returns full country name. Frontend only has country code.
   - What's unclear: Should frontend maintain country name mapping or should history event include country name?
   - Recommendation: History event already includes `country` field (from AttackEvent). Use `country` for display, `countryCode` for flag emoji. No mapping needed.

---

## Environment Availability

> Step 2.6: SKIPPED — This phase has no external dependencies beyond existing Python stdlib and Socket.io (already in use).

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python json module | Persistence | stdlib | N/A | — |
| Python os module | Atomic writes | stdlib | N/A | — |
| python-socketio | History event | Yes | 5.9.0+ | — |
| React Context | State management | Yes | 18+ | — |

**No missing dependencies.**

---

## Validation Architecture

> Workflow nyquist_validation is set to `false` in config.json. Skipping test framework section.

---

## Sources

### Primary (HIGH confidence)
- Python stdlib documentation (json, os.replace) — atomic file write pattern
- Existing codebase: main.py, SocketContext.tsx, StatsPanel.tsx — established patterns
- CONTEXT.md decisions D-01 through D-22 — locked implementation decisions

### Secondary (MEDIUM confidence)
- UI-SPEC.md — design specifications for new sections
- DESIGN.md — LED counter aesthetic, typography, spacing

### Tertiary (LOW confidence)
- None — all patterns are established in codebase or Python stdlib

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Uses existing dependencies, no new packages needed
- Architecture: HIGH — Follows established patterns from existing codebase
- Pitfalls: HIGH — Common issues well-documented in distributed systems literature

**Research date:** 2026-03-26
**Valid until:** 30 days (stable patterns, no fast-moving dependencies)