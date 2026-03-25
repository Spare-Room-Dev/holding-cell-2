# Phase 2: Core Visualization - Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

<domain>
## Phase Boundary

JailCellGrid displays prisoners in a stone-textured cell with iron bars overlay; StatsPanel shows attack counters with retro LED aesthetic. This phase delivers the static jail cell visualization and real-time stats panel — prisoner entrance animations and tooltips are Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Layout
- **D-01:** Sidebar layout with ~70% width for JailCellGrid, ~30% for StatsPanel (user clarified preference over full-width cell)
- **D-02:** JailCellGrid fills full viewport height minus header (immersive experience)
- **D-03:** StatsPanel scrolls independently if content overflows

### Cell Styling
- **D-04:** CSS-only stone/brick texture background using gradients and repeating patterns (no external image dependencies)
- **D-05:** Iron bar overlay via CSS repeating-linear-gradient (matches DESIGN.md direction)
- **D-06:** Dark theme primary — cell uses surface/background colors from DESIGN.md

### Prisoner Stack
- **D-07:** Fixed 20-slot grid — slots reserved, prisoners fill from bottom
- **D-08:** When count exceeds 20, oldest prisoner fades out via opacity transition
- **D-09:** Newest prisoners appear at top of stack (LIFO visual order)

### Prisoner Visual (Phase 3 Placeholder)
- **D-10:** Archetype-colored boxes as placeholder sprites until Phase 3 animated pixel-art
- **D-11:** Use existing ARCHETYPE_COLORS from page.tsx (phosphor, amber, alert, purple-400, blue-400)
- **D-12:** No hover tooltip in Phase 2 — that's Phase 3 (ArrestRecord component)

### Empty State
- **D-13:** "The cell is empty. Waiting for attackers..." styled with pixel font aesthetic
- **D-14:** CRT scanline overlay on empty state text (subtle retro effect)

### Stats Panel
- **D-15:** Horizontal row layout — 6 counters side-by-side (Total Attacks + 5 archetypes)
- **D-16:** StatsPanel positioned in sidebar (~30% width) next to JailCellGrid

### Counter Aesthetic
- **D-17:** Digital display boxes — numbers in segmented LCD-style boxes with dark background
- **D-18:** Phosphor green glow effect on active counter updates
- **D-19:** Numbers format with locale commas; display caps at 99,999+ (per STAT-04)
- **D-20:** Counter labels: "Total", "Script Kiddies", "APT Operatives", "Botnet Drones", "IoT Worms", "Hacktivists"

### Claude's Discretion
- Exact pixel dimensions for prisoner boxes (recommend 48-64px to leave room for Phase 3 sprite implementation)
- Exact transition timing for fade-out (recommend 200-300ms ease-out)
- Exact glow intensity for LED counter effect (follow DESIGN.md motion timing)
- Grid gap between prisoners in cell

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Decisions
- `PLAN.md` — Architecture diagram, component specs for JailCellGrid and StatsPanel, data model
- `DESIGN.md` — Color tokens (Phosphor Green `#00FF88`), typography (Satoshi, DM Sans, IBM Plex Mono), spacing scale, motion timing, border radius scale

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 2 requirements: CELL-01 to CELL-06, STAT-01 to STAT-04
- `.planning/PROJECT.md` — Tech stack, key decisions, aesthetic direction

### Prior Phase
- `.planning/phases/01-foundation/01-CONTEXT.md` — Phase 1 decisions (useReducer pattern, ARCHETYPE_COLORS, SocketContext)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/context/SocketContext.tsx` — useReducer pattern for attacks array, connection status
- `frontend/src/components/ConnectionStatus.tsx` — established pattern for status components
- `frontend/src/types/attack.ts` — AttackEvent interface, Archetype type
- `frontend/src/app/page.tsx` — ARCHETYPE_COLORS map, dashboard layout, placeholders for Phase 2 components

### Established Patterns
- useReducer for state management (scales better than useState per D-14 from Phase 1)
- Attacks array capped at 100 in SocketContext (memory management)
- Dark mode primary by default (D-16 from Phase 1)
- Framer Motion available for animations (Phase 3 entrance)

### Integration Points
- `JailCellGrid` connects to `useSocket()` for attacks array
- `StatsPanel` derives counts from attacks array in SocketContext
- Both components replace existing placeholders in `page.tsx`

</code_context>

<specifics>
## Specific Ideas

- Sidebar layout (70/30 split) places the cell as the creative centerpiece while stats remain visible
- Digital LED counters with phosphor green glow match the retro-futuristic aesthetic
- Fixed 20-slot grid provides predictable layout — easier to implement fade animation for overflow
- Archetype-colored boxes give visual variety while waiting for Phase 3 sprites
- CSS-only textures (no image assets) keeps bundle lean and load fast

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-core-visualization*
*Context gathered: 2026-03-25*