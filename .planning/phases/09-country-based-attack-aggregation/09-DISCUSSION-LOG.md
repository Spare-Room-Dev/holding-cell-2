# Phase 9: Country-based Attack Aggregation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 09-country-based-attack-aggregation
**Areas discussed:** Prisoner grouping model, Tooltip content & breakdown, Animation & visual behavior, Stats panel & data model

---

## Prisoner Grouping Model

| Option | Description | Selected |
|--------|-------------|----------|
| One slot per country | Each unique country gets one prisoner slot. New attacks from same country update the count. | ✓ |
| One slot per country + mini timeline | Each country gets one slot, tooltip has a mini timeline of last few attacks. | |
| Country slots with archetype indicators | Group by country, show multiple archetype-colored dots within each slot. | |

**User's choice:** One slot per country
**Notes:** Clean, matches the phase goal exactly. Simple to implement.

### Bandana Identity

| Option | Description | Selected |
|--------|-------------|----------|
| Dominant archetype color | Bandana shows the most frequent archetype from that country. | |
| Multi-dot archetype indicators | Small colored dots below prisoner showing top 2-3 archetypes. | |
| Country flag replaces bandana | Drop bandana entirely, show country flag emoji/icon instead. | ✓ |

**User's choice:** Country flag replaces bandana
**Notes:** Visual identity shifts from archetype to country. Country flag becomes the primary identifier.

### Grid Cap

| Option | Description | Selected |
|--------|-------------|----------|
| 20 countries (same as current) | Keep the 20-slot cap. Least-attacked fade out. | ✓ |
| No cap, show all countries | All countries shown, grid scrolls if needed. | |
| 30 countries | Expand to 30 slots. | |

**User's choice:** 20 countries (same cap as current)

---

## Tooltip Content & Breakdown

| Option | Description | Selected |
|--------|-------------|----------|
| Flag + count + archetype bars | Country flag + name, total count, archetype breakdown as colored horizontal bars. | ✓ |
| Flag + count + protocol breakdown | Country flag + name, total count, protocol breakdown (SSH vs Telnet). | |
| Flag + count + both breakdowns | Both archetype and protocol breakdowns. Most complete but potentially too dense. | |

**User's choice:** Flag + count + archetype bars

### Tooltip Style

| Option | Description | Selected |
|--------|-------------|----------|
| Terminal style (same as current) | Dark bg, phosphor green text, monospace. Consistent with existing design. | ✓ |
| Terminal style, wider for bars | Slightly wider to accommodate bars better. | |

**User's choice:** Terminal style (same as current)

---

## Animation & Visual Behavior

### New Country Entrance

| Option | Description | Selected |
|--------|-------------|----------|
| Spring entrance (same as current) | Same spring animation (y: -100, 300/20). Consistent. | ✓ |
| Enhanced entrance with flash | More dramatic entrance for new countries. | |

**User's choice:** Spring entrance (same as current)

### Update Animation

| Option | Description | Selected |
|--------|-------------|----------|
| Pulse/flash on update | Brief phosphor green glow when count increments. | ✓ |
| Count increment scale animation | Number scales up then back down. | |
| No animation, just update | Clean but loses visual feedback. | |

**User's choice:** Pulse/flash on update

### Grid Ordering

| Option | Description | Selected |
|--------|-------------|----------|
| Dynamic by attack count | Most-attacked at top/left, FLIP animation handles reordering. | ✓ |
| Fixed order (arrival order) | New countries appear at the end, never reorder. | |
| Arrival order with count badge | Fixed order with small count badge on each prisoner. | |

**User's choice:** Dynamic by attack count

---

## Stats Panel & Data Model

### CountryList

| Option | Description | Selected |
|--------|-------------|----------|
| Keep CountryList unchanged | Stats panel still shows top 5 countries numerically. Grid is the visual. | ✓ |
| Remove CountryList | Grid replaces it. | |
| Expand CountryList to detailed table | More info but significant stats panel change. | |

**User's choice:** Keep CountryList unchanged

### Data Model

| Option | Description | Selected |
|--------|-------------|----------|
| Derive on frontend | Group attacks by countryCode, compute archetype breakdown per country. No backend changes. | ✓ |
| New backend aggregation + socket event | Pre-computed country data sent via new socket event. | |

**User's choice:** Derive on frontend (no backend changes)

---

## Claude's Discretion

- Exact flag rendering approach (emoji vs SVG vs icon library)
- Pulse animation timing (recommend ~300ms)
- Tooltip bar width calculation (proportional to longest archetype)
- Grid reordering threshold (immediate on count change)
- Empty state text (stays the same)

## Deferred Ideas

None — discussion stayed within phase scope.