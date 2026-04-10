# Phase 9: Country-based Attack Aggregation — Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Pivot from one-prisoner-per-attack to one-prisoner-per-country. Each prisoner in the JailCellGrid represents a country of attack origin, with a hover tooltip showing attack count breakdown by archetype. The grid dynamically reorders by attack count and uses country flags for visual identity instead of archetype bandanas. Existing stats panel (CountryList, MethodsPanel) remains unchanged. Data is derived on the frontend from existing attack events and analytics — no backend changes required.

</domain>

<decisions>
## Implementation Decisions

### Prisoner Grouping Model
- **D-01:** One slot per country — each unique country gets one prisoner in the grid. New attacks from the same country update that prisoner's count rather than adding a new slot.
- **D-02:** Country flag replaces bandana color — prisoner identity shifts from archetype to country. The flag emoji/icon replaces the colored bandana as the primary visual identifier.
- **D-03:** 20-country cap (same as current 20-prisoner cap) — when exceeded, least-attacked countries fade out. Consistent with current grid behavior.

### Tooltip Content & Breakdown
- **D-04:** Tooltip shows country flag + country name, total attack count, and archetype breakdown as colored horizontal bars (script_kiddie: amber, botnet_drone: phosphor green, apt_operative: alert red, iot_worm: purple, hacktivist: blue). Visual and informative.
- **D-05:** Terminal aesthetic maintained — same dark bg, phosphor green text, monospace font as current ArrestRecordTooltip.

### Animation & Visual Behavior
- **D-06:** New countries get the same spring entrance animation as current prisoners (y: -100, spring 300/20). Consistent entrance experience.
- **D-07:** Pulse/flash effect on update — when an existing country's attack count increments, the prisoner gets a brief phosphor green glow pulse. Subtle but visible feedback without re-bouncing the slot.
- **D-08:** Dynamic ordering by attack count — most-attacked countries at top/left, least at bottom/right. FLIP animation (Framer Motion layout prop) handles smooth reordering.

### Stats Panel & Data Model
- **D-09:** CountryList in StatsPanel remains unchanged — it still shows top 5 countries by count as a numerical summary. The grid is the visual country representation; the stats panel is the numerical one.
- **D-10:** Derive country-prisoner data on the frontend — group existing attacks by countryCode, compute archetype breakdown per country from the attacks array. No backend changes needed; the existing `attack_event` and `analytics` data provides everything.

### Claude's Discretion
- Exact flag rendering approach (emoji vs SVG vs icon library) — recommend emoji for simplicity, consistent with existing `countryCodeToFlag()` function
- Exact pulse animation timing — recommend 300ms phosphor green glow, fading out
- Tooltip bar width calculation — recommend proportional bars where the longest archetype fills the available width, others scale proportionally
- Grid reordering threshold — recommend reordering immediately when counts change (FLIP handles the animation)
- Empty state text update — recommend "The cell is empty. Waiting for attackers..." stays the same
- How to handle the 20-country overflow — recommend fading out least-attacked countries (consistent with D-03)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture & Decisions
- `DESIGN.md` — Color tokens (archetype colors for bars), typography, spacing scale, motion timing
- `PLAN.md` — Architecture diagram, component specs, data model
- `.planning/PROJECT.md` — Tech stack, key decisions, aesthetic direction
- `.planning/REQUIREMENTS.md` — Phase 9 requirements (TBD)

### Prior Phases
- `.planning/phases/07-persistence-analytics/07-CONTEXT.md` — Analytics structure (countries, protocols, ports), persistence pattern
- `.planning/phases/06-cowrie-integration/06-CONTEXT.md` — Cowrie reader, GeoIP service, archetype classification
- `.planning/phases/03-animated-prisoners/03-CONTEXT.md` — Spring entrance animation specs, tooltip hover delay
- `.planning/phases/04-polish/04-CONTEXT.md` — Dark mode primary, LED counter aesthetic, responsive layout

### Existing Code
- `frontend/src/components/JailCellGrid.tsx` — Current per-attack grid rendering (needs refactor to per-country)
- `frontend/src/components/PrisonerSprite.tsx` — Pixel-art sprite with archetype bandana (needs country flag variant)
- `frontend/src/components/ArrestRecordTooltip.tsx` — Terminal-styled hover tooltip (needs country breakdown variant)
- `frontend/src/components/CountryList.tsx` — Top 5 countries by count (remains unchanged per D-09)
- `frontend/src/components/StatsPanel.tsx` — Analytics display (remains unchanged per D-09)
- `frontend/src/context/SocketContext.tsx` — Socket state with attacks[], analytics (derive country data from this)
- `frontend/src/types/attack.ts` — AttackEvent, Analytics, AttackHistoryPayload types
- `backend/persistence.py` — Analytics aggregation (countries, protocols, ports)
- `backend/models.py` — AttackEvent Pydantic model

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `PrisonerSprite.tsx` — Pixel-art SVG sprite component; needs a country-flag variant but keeps the same body/structure
- `ArrestRecordTooltip.tsx` — Terminal-styled tooltip; needs a country breakdown variant but reuses the layout pattern
- `CountryList.tsx` — Already renders country flags and names; unchanged per D-09
- `countryCodeToFlag()` (in `utils/countryToFlag.ts`) — Converts country codes to flag emoji; reusable for the grid
- `COUNTRY_NAMES` (in `CountryList.tsx`) — Country code-to-name mapping; needs to be extracted or shared
- `ARCHETYPE_COLORS` (in `ArrestRecordTooltip.tsx`) — Color mapping for archetype badges; reuse for tooltip bars
- `SocketContext.tsx` — Already tracks `attacks[]` and `analytics.countries`; derive country data from these

### Established Patterns
- Framer Motion `layout` prop for FLIP animations (already used in JailCellGrid)
- Spring physics entrance animation (stiffness: 300, damping: 20 for entrance)
- 150ms hover delay for tooltip display
- Dark terminal aesthetic for tooltips (`bg-[#1A1A1A]`, `border-[#00FF88]`, monospace font)
- `useSocket()` hook provides attacks array and analytics state

### Integration Points
- `JailCellGrid.tsx` — Main component to refactor from per-attack to per-country rendering
- `SocketContext.tsx` — Derive country-prisoner data from `state.attacks` grouped by `countryCode`
- `PrisonerSprite.tsx` — Add country flag rendering alongside or replacing the bandana
- `ArrestRecordTooltip.tsx` — Create a new `CountryTooltip` component or extend existing tooltip
- Stats panel remains unchanged — grid and stats are complementary views

</code_context>

<specifics>
## Specific Ideas

- Country flag as primary identifier: Use existing `countryCodeToFlag()` function for emoji flags rendered above/beside the sprite body
- Archetype breakdown bars in tooltip: Horizontal bars using `ARCHETYPE_COLORS` mapping — script_kiddie (amber #FFB800), botnet_drone (phosphor #00FF88), apt_operative (red #FF3B5C), iot_worm (purple #A855F7), hacktivist (blue #60A5FA)
- Pulse animation: Brief phosphor green glow (`rgba(0, 255, 136, 0.15)` background pulse) lasting ~300ms, triggered when attack count increments for that country
- FLIP reordering: Framer Motion `layout` prop on each country prisoner div enables smooth position transitions when attack counts reorder the grid
- Frontend data derivation: `useMemo` hook grouping `state.attacks` by `countryCode`, computing `{ countryCode, count, archetypes: { script_kiddie: N, ... }, lastAttack: timestamp }` for each country
- 20-country cap: After grouping and sorting, `slice(0, 20)` to keep the grid manageable; least-attacked countries naturally fall off the end

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 09-country-based-attack-aggregation*
*Context gathered: 2026-04-10*