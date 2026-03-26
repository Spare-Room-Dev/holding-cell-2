# Phase 6: Cowrie Integration — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 06-cowrie-integration
**Areas discussed:** OT Persona, GeoIP Source, Log Processing, Classification, Session Correlation, Event Timing, Fake Attacks, HASSH Source, Unknown HASSH, Cowrie Config

---

## OT Persona

| Option | Description | Selected |
|--------|-------------|----------|
| Heavy equipment manufacturer | motd shows CAT/Dresser equipment diagnostics, filesystem has /opt/caterpillar/ | |
| Oil & gas pipeline SCADA | motd shows pipeline pressure readings, filesystem has /var/scada/ | |
| **Mining automation system** | motd shows haul truck telemetry, filesystem has /var/mining/ | ✓ |
| Generic OT blend | Mix of industrial terms without specific vendor references | |

**User's choice:** Mining automation system — fits Perth OT cybersecurity positions targeting mining/industrial sector

---

## GeoIP Source

| Option | Description | Selected |
|--------|-------------|----------|
| **MaxMind GeoLite2 (free)** | Free database, requires account signup, monthly updates, 99.5% accuracy | ✓ |
| IP2Location Lite (free) | Free database, no signup required, less frequent updates | |
| Defer to Phase 7 | Use placeholder country codes for now | |

**User's choice:** MaxMind GeoLite2 — most accurate free option, standard choice for threat intelligence

---

## Log Processing

| Option | Description | Selected |
|--------|-------------|----------|
| **File tailing with async watcher** | Python watchdog or aiofiles tail — event-driven, low latency | ✓ (Claude's discretion) |
| Polling with interval | Read file every N seconds — simpler but higher latency | |

**User's choice:** Claude's discretion — file tailing is better for real-time event processing

---

## Archetype Classification

| Option | Description | Selected |
|--------|-------------|----------|
| **Pure HASSH + commands** | Use HASSH fingerprint (SSH client hash) + command sequence analysis | ✓ |
| Command patterns only | Match commands against ARCHETYPE_PROFILES patterns | |
| Duration + commands hybrid | Keep duration ranges from ARCHETYPE_PROFILES + add command pattern matching | |

**User's choice:** Pure HASSH + commands — per COW-04, most accurate classification approach

---

## Session Correlation

| Option | Description | Selected |
|--------|-------------|----------|
| **Emit on session close** | Emit only when session closes — complete data, accurate duration | ✓ |
| Stream events + finalize | Emit as events arrive, update existing attack on session close | |

**User's choice:** Emit on session close — simpler implementation, accurate duration calculation

---

## Event Timing

| Option | Description | Selected |
|--------|-------------|----------|
| Immediate emission | Show attacks immediately as they happen | |
| **Throttled (1-2s)** | Small delay to batch rapid attacks — prevents UI flooding | ✓ |

**User's choice:** Throttled (1-2s) — better UX, prevents dashboard overwhelm during attack spikes

---

## Fake Attacks

| Option | Description | Selected |
|--------|-------------|----------|
| **Show only real attacks** | Fake attacks stop entirely, dashboard waits for real attacks | ✓ |
| Mix real + fake (testing) | Mix real & fake during testing | |

**User's choice:** Show only real attacks — authentic threat intelligence dashboard

---

## HASSH Source

| Option | Description | Selected |
|--------|-------------|----------|
| **Extract from Cowrie log field** | Cowrie logs include a 'hassh' field for SSH sessions | ✓ (Claude's discretion) |
| Use hassh-lib python package | Use existing Python library to compute HASSH | |

**User's choice:** Claude's discretion — extract from Cowrie logs directly, simpler implementation

---

## Unknown HASSH Handling

| Option | Description | Selected |
|--------|-------------|----------|
| **Fall back to commands** | If HASSH doesn't match, use command patterns only | ✓ (Claude's discretion) |
| Default to script_kiddie | If classification fails, use 'script_kiddie' as safe default | |

**User's choice:** Claude's discretion — fall back to command patterns for graceful degradation

---

## Cowrie Configuration

| Option | Description | Selected |
|--------|-------------|----------|
| **Use official image + volume mounts** | Use cowrie/cowrie:latest image, mount config files via volume | ✓ (Claude's discretion) |
| Custom Dockerfile with persona | Build custom image with persona pre-configured | |

**User's choice:** Claude's discretion — official image + volume mounts follows Phase 5 pattern

---

## Claude's Discretion

- **Log Processing:** Async file tailing (watchdog or aiofiles) — event-driven, low latency
- **HASSH Source:** Extract from Cowrie log field directly — simpler, Cowrie already includes it
- **Unknown HASSH fallback:** Fall back to command patterns — graceful degradation, more accurate than defaulting
- **Cowrie Config:** Official image + volume mounts for motd/filesystem/usernames — follows Phase 5 pattern
- **Throttle interval:** 1.5 seconds as balance between responsiveness and UI performance

---

## Deferred Ideas

None — all discussion stayed within phase scope.