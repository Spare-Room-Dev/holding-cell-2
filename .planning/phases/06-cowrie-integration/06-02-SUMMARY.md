---
phase: 06-cowrie-integration
plan: 02
subsystem: backend
tags: [cowrie, geoip, hassh, watchfiles, async, session-correlation, archetypes]

# Dependency graph
requires:
  - phase: 05-docker-containerization
    provides: Docker Compose structure, Cowrie container, volume sharing
provides:
  - GeoIP service for IP-to-country enrichment
  - HASSH fingerprint mapping for attack classification
  - Cowrie log reader with async session correlation
affects: [06-03, main.py integration]

# Tech tracking
tech-stack:
  added: [watchfiles, geoip2]
  patterns: [async file watching, session correlation, HASSH classification]

key-files:
  created:
    - backend/geoip_service.py
    - backend/cowrie_reader.py
  modified:
    - backend/archetypes.py

key-decisions:
  - "D-05: watchfiles for async log watching (native async support)"
  - "D-09: Emit attacks on session close only for complete data"
  - "D-12: 1.5 second throttle to prevent UI flooding"
  - "D-14-D-19: HASSH fingerprint + command pattern classification"

patterns-established:
  - "Session correlation by session ID from Cowrie JSON logs"
  - "HASSH-first classification with command pattern fallback"
  - "GeoIP lookup with graceful fallback to Unknown/XX"

requirements-completed: [COW-02, COW-03, COW-04, COW-05]

# Metrics
duration: 4min
completed: 2026-03-26
---

# Phase 06 Plan 02: Cowrie Reader Implementation Summary

**GeoIP service, HASSH fingerprint mapping, and async Cowrie log reader with session correlation for real-time attack processing**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-26T13:14:42Z
- **Completed:** 2026-03-26T13:18:16Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- GeoIP lookup service using MaxMind GeoLite2 with graceful fallback
- HASSH fingerprint mapping for SSH client identification (all 5 archetypes)
- Async Cowrie log reader with session correlation and throttled emission
- Command pattern classification for Telnet and unknown HASSH sessions

## Task Commits

Each task was committed atomically:

1. **Task 1: Create GeoIP Service Module** - `ceac2d4` (feat)
2. **Task 2: Update archetypes.py with HASSH Fingerprint Mapping** - `cc2cf2d` (feat)
3. **Task 3: Create Cowrie Reader Module** - `a5a744c` (feat)

## Files Created/Modified
- `backend/geoip_service.py` - MaxMind GeoLite2 country lookup service with fallback
- `backend/archetypes.py` - Added KNOWN_HASSH dictionary and classification functions
- `backend/cowrie_reader.py` - Async log watcher with session correlation

## Decisions Made
- Used `watchfiles.awatch()` for native async file watching (per D-05)
- Emit attacks only on `cowrie.session.closed` for complete data (per D-09)
- 1.5 second throttle interval to balance UI smoothness with attack bursts (per D-12)
- HASSH-first classification with command pattern fallback for Telnet/unknown fingerprints (per D-14-D-19)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None - all implementations followed the plan specifications.

## User Setup Required
None - no external service configuration required for this plan. Note: GeoLite2 database must be downloaded and mounted for production use (documented in RESEARCH.md).

## Next Phase Readiness
- Ready for main.py integration to replace attack_generator.py
- GeoIP service ready for country enrichment
- Session correlation ready for real-time attack processing
- Classification ready for all 5 archetypes

---
*Phase: 06-cowrie-integration*
*Completed: 2026-03-26*

## Self-Check: PASSED
- backend/geoip_service.py: FOUND
- backend/cowrie_reader.py: FOUND
- backend/archetypes.py: FOUND (modified)
- Commits verified: ceac2d4, cc2cf2d, a5a744c