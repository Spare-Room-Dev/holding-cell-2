# Phase 4: Polish — Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

## Overview
This phase makes the dashboard responsive, verifies archetype classification end-to-end, ensures demo-ready polish, and adds mobile support. The core visualization (prisoners, animations, tooltips) is complete from Phase 3.

## Prior Decisions Applied
- **D-16 (Phase 1):** Dark mode primary by default
- **D-01 (Phase 2):** 70/30 sidebar layout (now needs responsive breakpoint)
- **D-17-D-20 (Phase 2):** LED counter aesthetic with phosphor glow
- **D-17 (Phase 3):** Spring entrance animation (300/20 entrance, 400/25 shift)
- **D-16 (Phase 3):** Tooltip terminal styling with 150ms hover delay

---

<domain>
## Phase Boundary

MVP ships with responsive layout, working archetype classification, and demo-ready experience. This phase delivers polish for recruiter demos — responsive breakpoints, light mode toggle, verification of classification rules, and empty/disconnect state UX. No new features beyond polish and responsiveness.

</domain>

<decisions>
## Implementation Decisions

### Responsive Layout
- **D-01:** Desktop layout (≥1024px): Current 70/30 sidebar remains unchanged
- **D-02:** Tablet/small desktop (768px-1023px): Stack stats below JailCellGrid (100% width each)
- **D-03:** Mobile (<768px): Full responsive with stats in bottom sheet overlay
- **D-04:** Below 320px: Minimum supported width — layout may break below this

### Mobile Stats Panel
- **D-05:** Stats hidden by default on mobile (<768px)
- **D-06:** "Stats" button in header opens bottom sheet overlay
- **D-07:** Bottom sheet uses slide-up animation with backdrop
- **D-08:** Tap outside or swipe down dismisses sheet

### Light Mode
- **D-09:** Toggle button in header (next to connection status)
- **D-10:** Uses CSS custom properties for theme switching
- **D-11:** Light mode colors from DESIGN.md: background `#F5F4F0`, surface `#FFFFFF`, borders `#E0DDD5`, accents desaturated ~15%
- **D-12:** No localStorage persistence in Phase 4 — default to dark on each visit

### Demo-Ready Verification
- **D-13:** Verify empty state displays correctly ("The cell is empty. Waiting for attackers...")
- **D-14:** Verify disconnect UX ("SIGNAL LOST" banner, LIVE badge behavior)
- **D-15:** Verify archetype classification produces correct archetypes per BACK-08 rules
- **D-16:** Manual testing verification — no automated tests in this phase

### Number Formatting
- **D-17:** Counters use `toLocaleString()` for comma formatting
- **D-18:** Counter display caps at 99,999+ (per STAT-04) — verify existing CounterBox implementation

### Claude's Discretion
- Exact breakpoint values (recommend Tailwind `md:` and `lg:` breakpoints)
- Animation timing for bottom sheet (recommend DESIGN.md motion timing: 250-400ms)
- Exact light mode toggle placement in header
- Whether to add `prefers-color-scheme` detection (recommend: no, stick with explicit toggle)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Decisions
- `PLAN.md` — Architecture diagram, component specs, data model
- `DESIGN.md` — Color tokens (including light mode colors), typography, spacing scale, motion timing, border radius scale

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 4 success criteria (responsive, archetype classification, light mode, number formatting)
- `.planning/PROJECT.md` — Tech stack, key decisions, aesthetic direction

### Prior Phases
- `.planning/phases/01-foundation/01-CONTEXT.md` — useReducer pattern, SocketContext, dark mode default
- `.planning/phases/02-core-visualization/02-CONTEXT.md` — 70/30 layout, CSS textures, LED counters
- `.planning/phases/03-animated-prisoners/03-CONTEXT.md` — Sprite implementation, entrance animation, tooltip styling

### Classification Rules
- `backend/archetypes.py` — ARCHETYPE_PROFILES with fingerprint rules (script_kiddie <2min/<10cmds, botnet_drone repeated passwords, apt_operative >10min/>50cmds with recon, iot_worm buildroot/busybox/mips, hacktivist anonymous/free/hack in username)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/app/page.tsx` — 70/30 flex layout, needs responsive breakpoint classes
- `frontend/src/components/StatsPanel.tsx` — Counter row with flex-wrap, can be extracted for bottom sheet
- `frontend/src/components/JailCellGrid.tsx` — Empty state already implemented
- `frontend/src/components/ConnectionStatus.tsx` — LIVE badge and disconnect UI already implemented
- `frontend/src/components/CounterBox.tsx` — Counter display component

### Established Patterns
- Tailwind CSS with custom design tokens (colors, spacing defined in DESIGN.md)
- Framer Motion for animations (use for bottom sheet slide-up)
- CSS custom properties for theming (already defined in globals.css)
- `useSocket()` hook provides attacks array for StatsPanel

### Integration Points
- Light mode toggle: Add to header in `page.tsx` or `ConnectionStatus.tsx`
- Bottom sheet: New component wrapping StatsPanel content
- Responsive layout: Add Tailwind breakpoint classes to `page.tsx` container
- Counter formatting: Verify/fix `CounterBox.tsx` to use `toLocaleString()`

</code_context>

<specifics>
## Specific Ideas

- Bottom sheet pattern is common in mobile apps (Instagram, Twitter) — familiar UX for mobile stats
- Light mode toggle as a simple sun/moon icon button — minimal header footprint
- StatsPanel content can be extracted into a shared component used by both sidebar and bottom sheet
- 320px minimum matches iPhone SE viewport — reasonable floor for mobile support
- Manual archetype verification: run backend, watch console logs, verify classification matches duration/command patterns

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-polish*
*Context gathered: 2026-03-25*