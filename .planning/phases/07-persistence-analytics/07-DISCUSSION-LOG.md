# Phase 7: Persistence & Analytics — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 07-persistence-analytics
**Areas discussed:** Storage, UI Layout, Analytics, Connection, Top Countries, Counter, Persistence, Aggregation

---

## Storage Approach

| Option | Description | Selected |
|--------|-------------|----------|
| JSON file (recommended) | Simple, Docker volume-friendly, easy to inspect. Already using volume pattern for Cowrie logs. | ✓ |
| SQLite | More queryable for analytics, but adds DB dependency and complexity. | |
| Redis | Fast in-memory with persistence, but adds Redis container. Overkill for 20 items. | |

**User's choice:** JSON file (recommended)
**Notes:** Consistent with existing Docker volume pattern from Phase 5.

---

## UI Layout for Analytics

| Option | Description | Selected |
|--------|-------------|----------|
| Extend StatsPanel (recommended) | Add new sections below existing archetype counters. Consistent LED aesthetic, no new components needed. | ✓ |
| New AnalyticsPanel component | Separate panel on the right side. More visual distinction. | |
| Bottom section below jail cell | Full-width analytics bar at the bottom. Changes layout significantly. | |

**User's choice:** Extend StatsPanel (recommended)
**Notes:** Keeps UI unified, reuses LED counter aesthetic.

---

## Attack Methods Tracking (STAT-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Protocol + Port breakdown (recommended) | SSH vs Telnet, then top 5 ports targeted. Simple and clear. | ✓ |
| Protocol + Port + Command patterns | More detailed breakdown including command patterns. More complex. | |
| Protocol only | Just SSH vs Telnet counts. May feel incomplete. | |

**User's choice:** Protocol + Port breakdown (recommended)
**Notes:** Covers STAT-03 requirement simply.

---

## Connection History Delivery

| Option | Description | Selected |
|--------|-------------|----------|
| Emit history on socket connect (recommended) | Server sends last 20 attacks on connect via `attack_history` event. Simple, immediate. | ✓ |
| HTTP endpoint on page load | Frontend fetches /api/history on mount, then switches to Socket.io. More code. | |

**User's choice:** Emit history on socket connect (recommended)
**Notes:** Works with current architecture, immediate on connect.

---

## Top Attacking Locations

| Option | Description | Selected |
|--------|-------------|----------|
| Top 5 countries (recommended) | Show top 5 attacking countries by attack count. Simple leaderboard. | ✓ |
| All countries | Show all countries with counts. Could get very long. | |
| Top 3 countries | Minimal, but may feel incomplete. | |

**User's choice:** Top 5 countries (recommended)
**Notes:** Covers STAT-02 requirement appropriately.

---

## Lifetime Counter Reset

| Option | Description | Selected |
|--------|-------------|----------|
| Cumulative from deployment (recommended) | Counter starts at 0 and increments forever. Simple, reflects real count. | ✓ |
| Allow manual reset | Add reset button or API. More flexibility but more complexity. | |

**User's choice:** Cumulative from deployment (recommended)
**Notes:** No reset functionality needed.

---

## Persistence Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Persist every attack (recommended) | Write to JSON after every attack. Survives restart, minimal code. | ✓ |
| Batch writes (interval) | Keep in memory, flush periodically. Less disk I/O but risk of data loss. | |

**User's choice:** Persist every attack (recommended)
**Notes:** No data loss on crash, simple implementation.

---

## Analytics Aggregation

| Option | Description | Selected |
|--------|-------------|----------|
| Real-time incremental (recommended) | Track in memory as attacks come in, recompute on startup. O(1) updates. | ✓ |
| On-demand calculation | Compute counts from scratch on each request. Could be slow. | |

**User's choice:** Real-time incremental (recommended)
**Notes:** Efficient, persist aggregations with history JSON.

---

## Claude's Discretion

Areas where user deferred to Claude:
- Exact JSON file structure
- Exact aggregation schema
- Exact StatsPanel section placement
- Error handling for corrupted JSON

---

## Deferred Ideas

None — discussion stayed within phase scope.