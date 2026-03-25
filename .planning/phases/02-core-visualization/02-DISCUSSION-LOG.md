# Phase 2: Core Visualization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-25
**Phase:** 02-core-visualization
**Areas discussed:** Layout, Cell Style, Stats Panel, Counter Style, Cell Height, Empty State, Prisoner Stack, Prisoner Visual

---

## Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Full-width cell | Prisoners stack from bottom in single column. Cell is creative centerpiece. Uses CSS Grid with auto-rows from bottom. | |
| Sidebar layout | Cell takes left ~60%, StatsPanel takes right ~40%. More traditional dashboard layout. | |

**User's choice:** Sidebar layout (clarified as ~70% cell, ~30% stats panel)
**Notes:** User prefers sidebar with 70% cell, 20% stats panel (remainder for spacing).

---

## Cell Style

| Option | Description | Selected |
|--------|-------------|----------|
| CSS-only textures | Use CSS gradients and repeating patterns to create stone/brick texture. No external image dependencies. Fast to load. | ✓ |
| SVG background patterns | Use SVG patterns for more detailed stone/brick texture. More control over appearance. | |
| Background images | Use raster images for texture. More realistic but requires asset management. | |

**User's choice:** CSS-only textures
**Notes:** Recommended option selected. Matches DESIGN.md direction.

---

## Stats Panel

| Option | Description | Selected |
|--------|-------------|----------|
| Horizontal row | One row with 6 counters (Total + 5 archetypes). Fits well at 1200px max-width. Classic dashboard feel. | ✓ |
| Grid layout (2x3) | 2 columns, 3 rows. More vertical space, larger counters. Good for smaller widths. | |
| Vertical column | One column, 6 counters. Takes more vertical space. Works if cell is wider. | |

**User's choice:** Horizontal row
**Notes:** Fits naturally in the ~30% sidebar next to cell.

---

## Counter Style

| Option | Description | Selected |
|--------|-------------|----------|
| Digital display boxes | Numbers displayed in segmented LCD-style boxes with dark background. True to retro LED counter aesthetic. | ✓ |
| Simple bold numbers with glow | Large phosphor-green numbers with glow effect. Matches the LIVE badge style. Simpler implementation. | |
| LCD seven-segment font | Seven-segment LCD font styling. Most authentic but requires specific font file. | |

**User's choice:** Digital display boxes
**Notes:** LED aesthetic with dark background boxes.

---

## Cell Height

| Option | Description | Selected |
|--------|-------------|----------|
| Full viewport height | Cell fills available viewport minus header. Stats panel scrolls independently if needed. Full immersion. | ✓ |
| Fixed height (600px) | Fixed 600px cell height. More controlled, leaves room for other content below. | |
| Auto-grow with content | Cell grows with content (prisoner count). Could get very tall if many attacks. | |

**User's choice:** Full viewport height
**Notes:** Immersive experience. Stats can scroll independently.

---

## Empty State

| Option | Description | Selected |
|--------|-------------|----------|
| Pixel font with CRT scanlines | Use pixel-art style font for the empty message. Subtle, reinforces theme. | ✓ |
| Monospace with terminal styling | IBM Plex Mono with phosphor green text. Matches terminal aesthetic. | |
| Clean body text | DM Sans with muted styling. Clean and simple. | |

**User's choice:** Pixel font with CRT scanlines
**Notes:** Matches retro-futuristic aesthetic. DESIGN.md typography scale for pixel-style rendering.

---

## Prisoner Stack

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed 20-slot grid | 20 slots reserved in grid, prisoners fill from bottom. Older ones fade via opacity transition when count exceeds 20. | ✓ |
| Dynamic list with removal | Prisoners added dynamically, oldest removed when count exceeds 20. Simpler but no fade animation. | |
| Flex column reversed | Single column flex container, newest on top, 20 max. Fade implemented on overflow. | |

**User's choice:** Fixed 20-slot grid
**Notes:** Predictable layout, easier fade animation implementation.

---

## Prisoner Visual (Phase 3 Placeholder)

| Option | Description | Selected |
|--------|-------------|----------|
| Simple placeholder boxes | Placeholder boxes with archetype name and IP. No sprites yet. Clean implementation, sprites added in Phase 3. | |
| Archetype-colored boxes | Colored boxes based on archetype. Slightly more visual but still no sprites. | ✓ |

**User's choice:** Archetype-colored boxes
**Notes:** Uses existing ARCHETYPE_COLORS from page.tsx for visual variety. Sprites and animations are Phase 3.

---

## Claude's Discretion

- Exact pixel dimensions for prisoner boxes (recommend 48-64px)
- Exact transition timing for fade-out (recommend 200-300ms ease-out)
- Exact glow intensity for LED counter effect
- Grid gap between prisoners in cell

## Deferred Ideas

None — discussion stayed within phase scope.