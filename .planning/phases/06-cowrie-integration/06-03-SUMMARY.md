---
phase: 06-cowrie-integration
plan: 03
subsystem: backend
tags: [cowrie, integration, socketio, geoip]
requires: [06-01, 06-02]
provides: [real-attack-flow]
affects: [backend/main.py, backend/attack_generator.py, README.md]
duration: 3m
completed: 2026-03-26T13:26:10Z
key-decisions:
  - D-07: CowrieReader replaces attack_generator for real data
  - D-08: Fake attack generator disabled entirely
  - D-13: Same attack_event Socket.io channel (frontend unchanged)
---

# Phase 06 Plan 03: Cowrie Backend Integration Summary

## One-Liner

Integrated CowrieReader into FastAPI backend, replacing fake attack generator with real honeypot data flow, and added GeoIP setup documentation.

## What Was Done

### Task 1: Update main.py to Use CowrieReader

- Replaced `attack_generator` import with `CowrieReader` and `GeoIPService` imports
- Added module-level `geoip_service` and `cowrie_reader` variables
- Replaced `attack_emitter()` background task with `cowrie_emitter()`:
  - Initializes GeoIPService on startup
  - Initializes CowrieReader with GeoIP service
  - Processes existing log entries first (captures pre-restart sessions)
  - Watches for new log entries via `watch_log()`
  - Emits attacks via Socket.io `attack_event` channel
- Updated startup event to create `cowrie_emitter` task

### Task 2: Disable Fake Attack Generator

- Added DEPRECATED docstring explaining module is no longer used
- Added `DISABLED = True` module-level flag
- Modified `generate_fake_attack()` to raise `RuntimeError` when `DISABLED`
- Module can be re-enabled for testing by setting `DISABLED = False`

### Task 3: Add GeoIP Directory Setup Instructions

- Created README.md with:
  - Quick start section with docker-compose commands
  - GeoIP setup section with MaxMind account signup steps
  - Fallback behavior documentation for missing database
  - Docker Compose volume mount configuration example

## Files Modified

| File | Change |
|------|--------|
| `backend/main.py` | Replaced attack_emitter with cowrie_emitter, added CowrieReader/GeoIPService imports |
| `backend/attack_generator.py` | Added DISABLED flag and RuntimeError, deprecated module |
| `README.md` | Created with GeoIP setup instructions |

## Key Decisions

- **D-07**: CowrieReader replaces attack_generator — real attacks flow from Cowrie honeypot
- **D-08**: Fake attack generator disabled — dashboard shows only real attacks
- **D-13**: Same `attack_event` Socket.io channel — frontend unchanged

## Verification Results

All automated verification passed:

```
PASS: main.py updated for Cowrie integration
PASS: attack_generator.py disabled
PASS: README.md has GeoIP setup instructions
```

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Commit | Message |
|--------|---------|
| `1932375` | feat(06-03): integrate CowrieReader and disable fake attack generator |
| `1a1a3c6` | fix(06-03): disable fake attack generator |
| `26853ec` | docs(06-03): add GeoIP setup instructions to README |

## Next Steps

With this plan complete:
- Backend now reads real Cowrie attacks via `cowrie_reader.py`
- Socket.io emits real attack events on `attack_event` channel
- Frontend receives real attack data with correct archetype classification and GeoIP country

Remaining Phase 06 plans: None (Plan 03 was the last plan in this phase)

## Self-Check: PASSED

- [x] `backend/main.py` exists with CowrieReader import
- [x] `backend/attack_generator.py` has DISABLED = True
- [x] `README.md` exists with GeoIP setup section
- [x] Commits exist: 1932375, 1a1a3c6, 26853ec