# Phase 4: Polish — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-25
**Phase:** 04-polish
**Areas discussed:** Layout, Light Mode, Demo Ready, Verification, Mobile

---

## Layout Responsive

| Option | Description | Selected |
|--------|-------------|----------|
| Collapse sidebar to 20% width | Keep sidebar visible but narrower. Simpler, works at 1024px+. Mobile is Weekend 2. | |
| Stack stats below cell at <1024px | Move stats below the cell on narrow screens. Requires more layout work but better mobile experience if scope expands. | ✓ |
| Keep current layout at all sizes | Horizontal scroll is acceptable for portfolio demo. No responsive work this phase. | |

**User's choice:** Stack stats below cell at <1024px
**Notes:** User wants full responsive support, not just desktop max-width fix.

---

## Light Mode Toggle

| Option | Description | Selected |
|--------|-------------|----------|
| Header toggle button (Recommended) | Simple toggle button in header. CSS variables for themes already in DESIGN.md. Light mode is secondary but functional. | ✓ |
| Toggle with localStorage persistence | Persist preference in localStorage. More polish but adds scope. | |
| Skip light mode this phase | Light mode is not a portfolio demo requirement. Focus on responsive and archetype verification. | |

**User's choice:** Header toggle button
**Notes:** Recommended approach selected. No localStorage persistence in this phase.

---

## Demo Ready

| Option | Description | Selected |
|--------|-------------|----------|
| Verify empty states + disconnect UX (Recommended) | Verify current implementation handles these gracefully. No new features. | ✓ |
| Add demo speed mode (1-2s interval) | Add a 'speed up attacks' mode for demo purposes. Adds scope but impressive for presentations. | |
| Comprehensive demo polish | Full polish: demo mode + error boundaries + retry UX. Larger scope. | |

**User's choice:** Verify empty states + disconnect UX
**Notes:** Manual verification approach. No new features needed.

---

## Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Verify with manual testing (Recommended) | Code review confirms rules match. Success criteria satisfied. | ✓ |
| Add automated classification tests | Add unit tests for archetype profiles. More thorough but adds scope. | |
| Trust the implementation | The fake data generator is internal and working. Focus on layout and demo. | |

**User's choice:** Verify with manual testing
**Notes:** Backend archetypes.py already has correct fingerprint rules. Manual verification suffices.

---

## Mobile Below 768px

| Option | Description | Selected |
|--------|-------------|----------|
| Block with desktop-only message (Recommended) | Show 'Dashboard requires desktop browser' message below 768px. Simple scope, clear UX. | |
| Allow any viewport | Let layout flow naturally below 768px. May not look polished but functional. | |
| Full mobile responsive | Handle 320px-768px with hamburger menu for stats. Larger scope but better portfolio signal. | ✓ |

**User's choice:** Full mobile responsive
**Notes:** User wants full mobile support for portfolio demo impressiveness.

---

## Stats on Mobile

| Option | Description | Selected |
|--------|-------------|----------|
| Bottom sheet overlay (Recommended) | Hide stats, show 'Stats' button that opens bottom sheet. Clean mobile UX, common pattern. | ✓ |
| Stack below cell with scroll | Stats push cell up, scrollable below. Simpler but less polished on small screens. | |
| Tab-based navigation | Stats in separate screen, nav tab to switch. More app-like, adds routing scope. | |

**User's choice:** Bottom sheet overlay
**Notes:** Recommended approach selected. Uses slide-up animation with backdrop.

---

## Claude's Discretion

Areas where Claude has flexibility:
- Exact breakpoint values (recommend Tailwind `md:` and `lg:`)
- Animation timing for bottom sheet (recommend DESIGN.md motion timing: 250-400ms)
- Exact light mode toggle placement in header
- `prefers-color-scheme` detection (recommend: no, explicit toggle)

---

## Deferred Ideas

None — discussion stayed within phase scope.