# Phase 3: Animated Prisoners — Context

## Overview
This phase transforms placeholder archetype-colored boxes into pixel-art prisoner sprites with Framer Motion entrance animations and interactive tooltips showing arrest records.

## Prior Decisions Applied
- **D-04:** Framer Motion available for animations
- **D-10:** Phase 2 used archetype-colored boxes as placeholders — this phase replaces them
- **D-11:** Use existing ARCHETYPE_COLORS pattern for archetype mapping
- **D-12:** No hover tooltip in Phase 2 — this phase adds it
- **Design System:** Pixel-art prisoners with colored bandanas, inline SVG (no external images), terminal aesthetic for tooltips

## Phase 3 Decisions

### D-14: Sprite Implementation
**Decision:** Inline SVG sprites per archetype (no external image files).

**Rationale:**
- Matches DESIGN.md direction directly
- Keeps bundle self-contained (no image files to manage)
- Enables future animation tweaks (e.g., bandana flutter)
- Tree-shakeable via React component props
- 5 separate SVGs at ~2-4KB each — acceptable bundle impact

**Implementation:**
- Create `PrisonerSprite` component with 5 archetype variants
- Render 32x32 pixel-art SVG scaled to 56x56 display with `image-rendering: pixelated`
- Each sprite is inline in the component file

---

### D-15: Bandana Colors
**Decision:** Bandana colors match archetype (fixed colors from ARCHETYPE_COLORS).

**Rationale:**
- Preserves archetype-at-a-glance recognition
- Simpler implementation (no random logic)
- Aligns with existing ARCHETYPE_COLORS pattern
- Visual consistency — same archetype always same color

**Implementation:**
- Use existing `ARCHETYPE_COLORS` mapping from PrisonerSlot
- Bandana color applied to sprite's bandana pixel region
- Archetype colors:
  - `script_kiddie: 'amber'`
  - `botnet_drone: 'phosphor'`
  - `apt_operative: 'alert'`
  - `iot_worm: 'purple-400'`
  - `hacktivist: 'blue-400'`

---

### D-16: Tooltip Behavior
**Decision:** Tooltip shows on 150ms hover delay, positioned above avatar, terminal styling.

**Rationale:**
- 150ms delay prevents flicker when mouse passes quickly
- Position above avatar avoids cell edge clipping (newest prisoners at top)
- Matches DESIGN.md hover transition timing (150ms)
- Terminal aesthetic reinforces retro-futuristic theme

**Implementation:**
- Trigger: 150ms hover delay before show
- Position: Fixed above avatar (Y: -8px from avatar top)
- Dismiss: Immediate on mouse leave
- Width: Fixed 280px
- Style:
  - Background: `#1A1A1A` (surface)
  - Border: 1px solid `#00FF88` (phosphor)
  - Font: IBM Plex Mono 14px
  - Border-radius: 8px
  - Padding: 12px
- Content: ArrestRecord showing archetype, IP, country, port, protocol, commands, duration

---

### D-17: Entrance Animation
**Decision:** New prisoners enter from above with spring; existing prisoners shift down with stiffer spring.

**Rationale:**
- Entry from above matches DESIGN.md "flies in from above"
- Spring params (stiffness:300, damping:20) produce ~1.5 bounces — "wow moment"
- Stiffer spring on existing prisoners avoids overlapping bounce chaos
- Staggered movement creates visual hierarchy

**Implementation:**
- New prisoner animation:
  - Initial: `y: -100px, opacity: 0`
  - Animate: `y: 0, opacity: 1`
  - Transition: `type: 'spring', stiffness: 300, damping: 20`
- Existing prisoners shift:
  - Animate Y by +64px (56px avatar + 8px gap)
  - Transition: `type: 'spring', stiffness: 400, damping: 25` (stiffer, less bouncy)
- Use Framer Motion `layout` prop for automatic shift animation

---

## Technical Constraints
- **Framer Motion:** Already available (D-04), use for all animations
- **AnimatePresence:** Already used in JailCellGrid for enter/exit animations
- **No external images:** Per DESIGN.md, all sprites inline SVG
- **Type safety:** AttackEvent interface already defined in `frontend/src/types/attack.ts`
- **Component structure:**
  - `PrisonerSprite.tsx` — new, renders inline SVG per archetype
  - `PrisonerSlot.tsx` — update to use PrisonerSprite + AnimatePresence layout
  - `ArrestRecordTooltip.tsx` — new, hover tooltip component

## Dependencies
- No new dependencies required
- Reuses existing: Framer Motion, Tailwind CSS, ARCHETYPE_COLORS

## Edge Cases
- **Empty cell:** No prisoners → show empty cell background (no animation)
- **Cell full:** LIFO behavior defined in Phase 2 — oldest prisoner pushed out
- **Rapid attacks:** Spring animations handle rapid stacking gracefully
- **Tooltip overflow:** Position above ensures tooltip stays within viewport for newest prisoners

## Success Criteria Alignment
| Requirement | Decision |
|-------------|----------|
| PRSN-01: Prisoner avatars enter with Framer Motion spring physics | D-17 |
| PRSN-02: Spring params (stiffness:300, damping:20) | D-17 |
| PRSN-03: Hover shows ArrestRecord tooltip | D-16 |
| PRSN-04: Tooltip shows archetype, IP, country, port, protocol, commands, duration | D-16 |
| PRSN-05: Pixel-art sprites with colored bandanas | D-14, D-15 |
| PRSN-06: Inline SVG (no external images) | D-14 |
| TOOL-01: Terminal aesthetic for tooltip | D-16 |
| TOOL-02: 150ms hover delay | D-16 |
| TOOL-03: Tooltip dismiss on mouse leave | D-16 |

## Files to Create/Modify
| File | Action | Description |
|------|--------|-------------|
| `frontend/src/components/PrisonerSprite.tsx` | Create | Inline SVG sprites for each archetype |
| `frontend/src/components/ArrestRecordTooltip.tsx` | Create | Hover tooltip component |
| `frontend/src/components/PrisonerSlot.tsx` | Modify | Replace placeholder with PrisonerSprite + tooltip |
| `frontend/src/components/JailCellGrid.tsx` | Modify | Add layout prop for shift animation |

## Next Steps
1. **Research phase** (if needed): No external research required — all decisions locked
2. **Plan phase:** Create detailed implementation plan with task breakdown
3. **Execute phase:** Implement PrisonerSprite, then tooltip, then integration