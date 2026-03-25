---
phase: 02-core-visualization
plan: 02
subsystem: StatsPanel
tags: [visualization, counters, real-time, LED-aesthetic]
requires: [frontend/src/context/SocketContext.tsx]
provides:
  - frontend/src/components/StatsPanel.tsx
  - frontend/src/components/CounterBox.tsx
affects: [frontend/src/app/globals.css]
tech-stack:
  added: []
  patterns: [useMemo aggregation, Framer Motion animation]
key-files:
  created:
    - frontend/src/components/StatsPanel.tsx
    - frontend/src/components/CounterBox.tsx
  modified:
    - frontend/src/app/globals.css
decisions:
  - Counter labels per D-20 specification
  - formatCount caps display at 99,999+
  - Framer Motion scale bump animation (1.0 -> 1.02 -> 1.0)
  - framer-motion import (not motion/react)
metrics:
  duration: 10min
  completed_date: 2026-03-25
  tasks: 3
  files: 3
---

# Phase 02 Plan 02: StatsPanel Summary

## One-liner

LED-style counter panel with phosphor green glow effect, displaying Total Attacks and 5 archetype counts with real-time updates via useMemo aggregation from SocketContext.

## Completed Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add counter CSS utilities to globals.css | 5dd66bf | frontend/src/app/globals.css |
| 2 | Create CounterBox component | 89ac61a | frontend/src/components/CounterBox.tsx |
| 3 | Create StatsPanel component | b1a1441 | frontend/src/components/StatsPanel.tsx |

## Requirements Met

- **STAT-01:** All 6 counters display (Total + 5 archetypes)
- **STAT-02:** LED counter aesthetic with dark background and phosphor glow
- **STAT-03:** Counters increment when attacks arrive (useMemo reacts to state.attacks)
- **STAT-04:** Numbers formatted with locale commas, capped at 99,999+

## Implementation Details

### CSS Utilities (Task 1)
Added three utility classes to `globals.css`:
- `.counter-box`: Dark background (#0a0a0a), border, monospace font, 80px min-width
- `.counter-number`: Phosphor green (#00FF88) with text-shadow glow effect
- `.counter-label`: Muted text color, small font size, centered

### CounterBox Component (Task 2)
- `formatCount(n)`: Returns locale-formatted string, caps at "99,999+" for values > 99,999
- Framer Motion `motion.div` with scale keyframes `[1, 1.02, 1]` on value change
- 150ms animation duration per DESIGN.md short timing

### StatsPanel Component (Task 3)
- Uses `useMemo` to compute total and byArchetype counts from `state.attacks`
- `ARCHETYPE_LABELS` constant matches D-20 specification
- Horizontal flex row layout with gap-md and flex-wrap

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed framer-motion import path**
- **Found during:** Task 2 build verification
- **Issue:** Used `motion/react` import which doesn't exist; project uses `framer-motion` package
- **Fix:** Changed import to `from 'framer-motion'`
- **Files modified:** frontend/src/components/CounterBox.tsx
- **Commit:** b1a1441

## Dependencies

- `useSocket()` from `@/context/SocketContext` (Phase 1)
- `Archetype` type from `@/types/attack` (Phase 1)
- `framer-motion` v12.38.0 (already in package.json)

## Build Verification

- TypeScript compilation: PASSED
- Next.js build: PASSED
- All STAT requirements: PASSED

---

## Self-Check: PASSED

- [x] frontend/src/components/StatsPanel.tsx exists
- [x] frontend/src/components/CounterBox.tsx exists
- [x] frontend/src/app/globals.css modified with counter utilities
- [x] Commit 5dd66bf exists
- [x] Commit 89ac61a exists
- [x] Commit b1a1441 exists