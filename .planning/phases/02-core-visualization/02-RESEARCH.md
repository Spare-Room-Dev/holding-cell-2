# Phase 2: Core Visualization - Research

**Researched:** 2026-03-25
**Domain:** CSS textures, Framer Motion animations, React component patterns
**Confidence:** HIGH

## Summary

Phase 2 implements the JailCellGrid (stone texture + iron bars + prisoner stack) and StatsPanel (LED-style counters with phosphor glow). Research confirms CSS-only techniques for textures and bars are well-established, Framer Motion's AnimatePresence handles exit animations correctly, and the existing SocketContext useReducer pattern provides the attack data needed for both components. The 70/30 sidebar layout and vertical stacking from bottom are achievable with flexbox `column-reverse`.

**Primary recommendation:** Use layered `repeating-linear-gradient` for both stone texture and iron bar overlay; use Framer Motion `AnimatePresence` with `exit={{ opacity: 0 }}` for prisoner fade-out; derive stats from `useSocket().state.attacks` array with memoized aggregation.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Sidebar layout with ~70% width for JailCellGrid, ~30% for StatsPanel
- **D-02:** JailCellGrid fills full viewport height minus header
- **D-03:** StatsPanel scrolls independently if content overflows
- **D-04:** CSS-only stone/brick texture background using gradients and repeating patterns (no external image dependencies)
- **D-05:** Iron bar overlay via CSS repeating-linear-gradient
- **D-06:** Dark theme primary — cell uses surface/background colors from DESIGN.md
- **D-07:** Fixed 20-slot grid — slots reserved, prisoners fill from bottom
- **D-08:** When count exceeds 20, oldest prisoner fades out via opacity transition
- **D-09:** Newest prisoners appear at top of stack (LIFO visual order)
- **D-10:** Archetype-colored boxes as placeholder sprites until Phase 3 animated pixel-art
- **D-11:** Use existing ARCHETYPE_COLORS from page.tsx
- **D-12:** No hover tooltip in Phase 2 — that's Phase 3
- **D-13:** "The cell is empty. Waiting for attackers..." styled with pixel font aesthetic
- **D-14:** CRT scanline overlay on empty state text (subtle retro effect)
- **D-15:** Horizontal row layout — 6 counters side-by-side
- **D-16:** StatsPanel positioned in sidebar (~30% width) next to JailCellGrid
- **D-17:** Digital display boxes — numbers in segmented LCD-style boxes with dark background
- **D-18:** Phosphor green glow effect on active counter updates
- **D-19:** Numbers format with locale commas; display caps at 99,999+ (per STAT-04)
- **D-20:** Counter labels: "Total", "Script Kiddies", "APT Operatives", "Botnet Drones", "IoT Worms", "Hacktivists"

### Claude's Discretion
- Exact pixel dimensions for prisoner boxes (recommend 48-64px to leave room for Phase 3 sprite implementation)
- Exact transition timing for fade-out (recommend 200-300ms ease-out)
- Exact glow intensity for LED counter effect (follow DESIGN.md motion timing)
- Grid gap between prisoners in cell

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CELL-01 | JailCellGrid renders dark stone/brick CSS texture background | CSS `repeating-linear-gradient` with layered patterns creates brick/mortar effect |
| CELL-02 | Iron bar SVG/CSS overlay covers the cell | CSS `repeating-linear-gradient` with sharp stops creates vertical bars; overlay via `::after` pseudo-element |
| CELL-03 | Prisoners stack vertically from bottom, newest on top | Flexbox `flex-direction: column-reverse` stacks from bottom; LIFO order in array ensures newest on top |
| CELL-04 | Cell capacity: last 20 prisoners displayed | `attacks.slice(0, 20)` limits display; fixed slots can use placeholder elements |
| CELL-05 | Prisoners older than 20 fade out gracefully (opacity transition) | Framer Motion `AnimatePresence` with `exit={{ opacity: 0 }}` handles unmount animation |
| CELL-06 | Empty state: pixel font aesthetic | IBM Plex Mono already loaded; CSS `font-variant-numeric: tabular-nums` for alignment |
| STAT-01 | Displays: Total Attacks + 5 archetypes | Derive from `useSocket().state.attacks`; aggregate by `attack.archetype` |
| STAT-02 | Retro LED counter aesthetic | Stacked `box-shadow` with dark container; optional segmented LCD font alternative |
| STAT-03 | Counters increment on each `attack_event` received | SocketContext already dispatches `NEW_ATTACK`; use `useMemo` to recompute counts |
| STAT-04 | Numbers format with locale commas; cap at 99,999+ | `count.toLocaleString()` for commas; conditional `99,999+` for overflow |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Framer Motion | 12.38.0 | Exit animations, prisoner fade-out | Already in package.json; AnimatePresence handles unmount animations |
| Tailwind CSS | 4.x | Styling, design tokens | Already configured with CSS custom properties matching DESIGN.md |
| React | 19.2.4 | Component architecture | App Router established in Phase 1 |
| Next.js | 16.2.1 | App Router, font loading | Already running |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| socket.io-client | 4.8.3 | Real-time attack events | Already connected via SocketContext |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CSS gradients for stone | SVG pattern | SVG requires external asset; CSS stays in bundle |
| Framer Motion exit | CSS transition + useEffect cleanup | Framer Motion handles unmount timing correctly; manual cleanup is error-prone |
| Flexbox column-reverse | CSS Grid auto-flow dense | Flexbox simpler for single-column stack; Grid overkill |

**Installation:**
No new dependencies required — all libraries already in `frontend/package.json`.

**Version verification:**
- Framer Motion: 12.38.0 (current npm)
- Next.js: 16.2.1 (current npm)
- React: 19.2.4 (current npm)

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
├── app/
│   └── page.tsx              # Dashboard (replace placeholders with JailCellGrid, StatsPanel)
├── components/
│   ├── ConnectionStatus.tsx  # (existing)
│   ├── JailCellGrid.tsx      # NEW: Stone texture + iron bars + prisoner stack
│   ├── StatsPanel.tsx        # NEW: LED counters
│   └── PrisonerSlot.tsx      # NEW: Archetype-colored box placeholder
├── context/
│   └── SocketContext.tsx     # (existing) provides attacks array
└── types/
    └── attack.ts             # (existing) AttackEvent, Archetype types
```

### Pattern 1: CSS Stone/Brick Texture Background
**What:** Create dark stone/brick texture using layered `repeating-linear-gradient` without external images
**When to use:** JailCellGrid background per CELL-01
**Example:**
```css
/* Brick pattern with mortar lines */
.cell-background {
  background-color: #1a1a1a;
  background-image:
    /* Horizontal mortar lines */
    repeating-linear-gradient(
      0deg,
      transparent 0px,
      transparent 20px,
      rgba(42, 42, 42, 0.5) 20px,
      rgba(42, 42, 42, 0.5) 24px
    ),
    /* Vertical mortar lines with offset for brick pattern */
    repeating-linear-gradient(
      90deg,
      transparent 0px,
      transparent 48px,
      rgba(42, 42, 42, 0.3) 48px,
      rgba(42, 42, 42, 0.3) 52px
    );
  background-size: 52px 24px;
}
```
**Source:** [CSS-Tricks repeating-linear-gradient](https://css-tricks.com/almanac/functions/r/repeating-linear-gradient/)

### Pattern 2: Iron Bar Overlay
**What:** Vertical iron bars using CSS gradient overlay with 3D shadow effect
**When to use:** JailCellGrid overlay per CELL-02
**Example:**
```css
/* Iron bars as overlay */
.cell-bars {
  position: relative;
}

.cell-bars::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    to right,
    transparent 0px,
    transparent 16px,      /* gap between bars */
    rgba(26, 26, 26, 0.95) 16px,  /* dark edge */
    rgba(60, 60, 60, 0.9) 18px,   /* highlight */
    rgba(40, 40, 40, 0.95) 20px    /* shadow edge */
  );
  pointer-events: none;  /* Allow clicks to pass through */
  z-index: 10;
}
```
**Source:** [CSS-Tricks Stripes in CSS](https://css-tricks.com/stripes-css/)

### Pattern 3: Framer Motion Exit Animation
**What:** Graceful fade-out when prisoner exceeds capacity
**When to use:** Prisoner removal per CELL-05
**Example:**
```tsx
import { motion, AnimatePresence } from 'motion/react';

// In JailCellGrid component
<AnimatePresence mode="popLayout">
  {visiblePrisoners.map((attack) => (
    <motion.div
      key={attack.id}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      {/* Prisoner slot content */}
    </motion.div>
  ))}
</AnimatePresence>
```
**Source:** [Framer Motion AnimatePresence Docs](https://motion.dev/docs/react-animate-presence)

### Pattern 4: LED Counter Glow Effect
**What:** Phosphor green glow on counter update using stacked box-shadow
**When to use:** StatsPanel counters per STAT-02, STAT-03
**Example:**
```css
.counter-box {
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 4px;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

.counter-box.active {
  box-shadow:
    0 0 8px rgba(0, 255, 136, 0.3),
    0 0 16px rgba(0, 255, 136, 0.15),
    inset 0 0 4px rgba(0, 255, 136, 0.1);
}

.counter-number {
  color: #00FF88;
  text-shadow:
    0 0 4px rgba(0, 255, 136, 0.5),
    0 0 8px rgba(0, 255, 136, 0.3);
}
```
**Source:** [CSS-Tricks Neon Text](https://css-tricks.com/how-to-create-neon-text-with-css/)

### Pattern 5: Bottom-Up Flexbox Stack
**What:** Stack prisoners from bottom using flex-direction: column-reverse
**When to use:** Prisoner ordering per CELL-03, CELL-07
**Example:**
```tsx
// Container stacks from bottom
<div className="flex flex-col-reverse gap-2 h-full">
  {attacks.slice(0, 20).map((attack) => (
    <PrisonerSlot key={attack.id} attack={attack} />
  ))}
</div>
```
**Source:** [MDN Ordering Flex Items](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Ordering_flex_items)

### Anti-Patterns to Avoid
- **Using external images for textures:** Violates D-04 (CSS-only requirement); adds bundle size
- **Array index as key in AnimatePresence:** Breaks exit animations; use `attack.id` (UUID)
- **Inline styles for complex gradients:** Hard to maintain; use Tailwind v4 `@utility` or CSS custom properties
- **Counting attacks on every render:** Use `useMemo` to aggregate archetype counts; prevents unnecessary recalculations

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Exit animations | Manual setTimeout + opacity | Framer Motion `AnimatePresence` | Handles unmount timing, prevents memory leaks, correct key tracking |
| Attack aggregation | useState + useEffect | `useMemo` with `attacks.reduce()` | Memoized computation; reactive to attack array changes |
| Prisoner ordering | Custom sort logic | `flex-direction: column-reverse` + array order | CSS handles visual order; simpler than reordering array |
| Glow effects | Multiple box-shadow classes | Tailwind utility or CSS custom property | Reusable, consistent with DESIGN.md tokens |

**Key insight:** The existing SocketContext already maintains the attacks array capped at 100. For the cell display, slice to 20 and use Framer Motion for exit animations. Do not duplicate state management.

## Runtime State Inventory

> This is a visualization phase with no rename/refactor/migration operations. Runtime state is managed by existing SocketContext.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — attacks array in SocketContext | Code edit only |
| Live service config | None — Socket.io already connected | No action |
| OS-registered state | None | No action |
| Secrets/env vars | None | No action |
| Build artifacts | None | No action |

**Note:** Phase 2 consumes data from Phase 1's SocketContext. No data migration required.

## Common Pitfalls

### Pitfall 1: AnimatePresence Key Mismatch
**What goes wrong:** Exit animations don't play because React uses array index as key, or keys change unexpectedly
**Why it happens:** AnimatePresence tracks components by `key` prop; if key changes or uses index, exit animation fails
**How to avoid:** Always use `attack.id` (UUID) as key; never use array index
**Warning signs:** Prisoners disappear instantly instead of fading; console warnings about duplicate keys

### Pitfall 2: Flexbox Accessibility with column-reverse
**What goes wrong:** Screen readers and keyboard navigation follow source order, not visual order
**Why it happens:** `flex-direction: column-reverse` only changes visual rendering
**How to avoid:** For this phase, prisoners are display-only (no interactive elements); Phase 3 should test tooltip keyboard navigation
**Warning signs:** Tab order doesn't match visual order

### Pitfall 3: Counter Update Flash
**What goes wrong:** Counter glow effect flickers or persists incorrectly
**Why it happens:** Glow is tied to state update but not properly cleared after animation
**How to avoid:** Use CSS animation with `animation-fill-mode: forwards` or Framer Motion's `animate` prop with timeout to remove glow class
**Warning signs:** Glow stays on permanently; glow doesn't appear on new attacks

### Pitfall 4: Background Pattern Performance
**What goes wrong:** Complex CSS gradients cause repaints on scroll/resize
**Why it happens:** Multiple layered gradients with large `background-size` can be GPU-intensive
**How to avoid:** Keep `background-size` small (brick pattern ~50px); use `will-change: transform` sparingly if needed
**Warning signs:** Janky scrolling on mobile; high GPU usage in devtools

### Pitfall 5: Number Formatting Edge Cases
**What goes wrong:** Numbers over 99,999 show scientific notation or overflow container
**Why it happens:** JavaScript `toLocaleString()` handles commas but not capping
**How to avoid:** Conditional formatting:
```tsx
const formatCount = (count: number): string => {
  if (count > 99999) return '99,999+';
  return count.toLocaleString();
};
```
**Warning signs:** Counters break layout at high values

## Code Examples

### CSS Stone/Brick Texture (Verified Pattern)
```css
/* Tailwind v4 @utility or globals.css */
.cell-texture {
  background-color: var(--color-surface);
  background-image:
    /* Brick offset rows */
    repeating-linear-gradient(
      0deg,
      transparent 0px,
      transparent 23px,
      rgba(42, 42, 42, 0.4) 23px,
      rgba(42, 42, 42, 0.4) 26px
    ),
    /* Vertical mortar - even rows */
    repeating-linear-gradient(
      90deg,
      transparent 0px,
      transparent 50px,
      rgba(42, 42, 42, 0.3) 50px,
      rgba(42, 42, 42, 0.3) 54px
    ),
    /* Vertical mortar - odd rows (offset) */
    repeating-linear-gradient(
      90deg,
      transparent 25px,
      transparent 75px,
      rgba(42, 42, 42, 0.3) 75px,
      rgba(42, 42, 42, 0.3) 79px
    );
  background-size: 50px 26px;
}
```
**Source:** CSS-Tricks repeating-linear-gradient pattern techniques

### Iron Bar Overlay (Verified Pattern)
```css
/* As ::after pseudo-element overlay */
.cell-bars::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    to right,
    transparent 0px,
    transparent 16px,
    /* Bar shadow/3D effect */
    rgba(20, 20, 20, 0.95) 16px,
    rgba(50, 50, 50, 0.9) 17px,
    rgba(40, 40, 40, 0.95) 18px
  );
  pointer-events: none;
  z-index: 10;
  border-radius: inherit;
}
```

### Prisoner Stack Component (Verified Pattern)
```tsx
// JailCellGrid.tsx
'use client';

import { motion, AnimatePresence } from 'motion/react';
import { useSocket } from '@/context/SocketContext';
import { PrisonerSlot } from './PrisonerSlot';

export function JailCellGrid() {
  const { state } = useSocket();
  const attacks = state.attacks;

  // Show last 20, newest first (LIFO)
  const visibleAttacks = attacks.slice(0, 20);

  return (
    <div className="relative h-full cell-texture rounded-lg overflow-hidden">
      {/* Iron bar overlay */}
      <div className="absolute inset-0 cell-bars" />

      {/* Empty state */}
      {visibleAttacks.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <p className="font-mono text-text-muted text-center px-lg">
            The cell is empty. Waiting for attackers...
          </p>
        </div>
      )}

      {/* Prisoner stack - flex-col-reverse stacks from bottom */}
      <div className="absolute inset-0 flex flex-col-reverse gap-2 p-md overflow-hidden">
        <AnimatePresence mode="popLayout">
          {visibleAttacks.map((attack) => (
            <motion.div
              key={attack.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
            >
              <PrisonerSlot attack={attack} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
```
**Source:** Framer Motion AnimatePresence documentation

### Counter Aggregation (Verified Pattern)
```tsx
// StatsPanel.tsx
'use client';

import { useMemo } from 'react';
import { useSocket } from '@/context/SocketContext';
import type { Archetype } from '@/types/attack';

const ARCHETYPE_LABELS: Record<Archetype, string> = {
  script_kiddie: 'Script Kiddies',
  apt_operative: 'APT Operatives',
  botnet_drone: 'Botnet Drones',
  iot_worm: 'IoT Worms',
  hacktivist: 'Hacktivists',
};

export function StatsPanel() {
  const { state } = useSocket();

  const counts = useMemo(() => {
    const total = state.attacks.length;
    const byArchetype = state.attacks.reduce((acc, attack) => {
      acc[attack.archetype] = (acc[attack.archetype] || 0) + 1;
      return acc;
    }, {} as Record<Archetype, number>);

    return { total, byArchetype };
  }, [state.attacks]);

  const formatCount = (n: number): string =>
    n > 99999 ? '99,999+' : n.toLocaleString();

  return (
    <div className="flex flex-row gap-md flex-wrap">
      {/* Total counter */}
      <CounterBox label="Total" value={counts.total} />

      {/* Archetype counters */}
      {Object.entries(ARCHETYPE_LABELS).map(([archetype, label]) => (
        <CounterBox
          key={archetype}
          label={label}
          value={counts.byArchetype[archetype as Archetype] || 0}
        />
      ))}
    </div>
  );
}
```

### LED Counter Box (Verified Pattern)
```tsx
// CounterBox.tsx
'use client';

import { motion } from 'motion/react';

interface CounterBoxProps {
  label: string;
  value: number;
}

const formatCount = (n: number): string =>
  n > 99999 ? '99,999+' : n.toLocaleString();

export function CounterBox({ label, value }: CounterBoxProps) {
  return (
    <div className="flex flex-col items-center gap-xs">
      <span className="text-text-muted text-label">{label}</span>
      <motion.div
        className="counter-box"
        initial={false}
        animate={{ scale: [1, 1.02, 1] }}
        transition={{ duration: 0.15 }}
      >
        <span className="counter-number font-mono text-mono">
          {formatCount(value)}
        </span>
      </motion.div>
    </div>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CSS background images | CSS `repeating-linear-gradient` patterns | 2018+ | No external assets, smaller bundles |
| setTimeout for exit animations | Framer Motion `AnimatePresence` | 2020+ | Correct unmount timing, no memory leaks |
| CSS transitions for lists | `mode="popLayout"` in AnimatePresence | 2022+ | Exiting elements don't block layout |
| Inline counters | Memoized aggregation with `useMemo` | React 18+ | Prevents unnecessary recalculations |

**Deprecated/outdated:**
- `react-transition-group`: Replaced by Framer Motion's built-in `AnimatePresence`
- CSS keyframe animations for exit: Can't detect when complete; use Framer Motion

## Open Questions

1. **Fixed 20-slot grid vs. dynamic slots**
   - What we know: D-07 specifies "fixed 20-slot grid — slots reserved, prisoners fill from bottom"
   - What's unclear: Should empty slots be visible placeholders, or should the grid grow as prisoners arrive?
   - Recommendation: Implement as dynamic list capped at 20 (simpler, matches Phase 1 `attacks.slice(0, 100)` pattern). Fixed empty slots add visual complexity without UX benefit.

2. **CRT scanline effect intensity**
   - What we know: D-14 specifies "subtle retro effect" for empty state text
   - What's unclear: Exact opacity and line height for scanlines
   - Recommendation: Use 1px horizontal lines at 4px intervals with 0.03 opacity — visible but not distracting

3. **Phosphor glow pulse on counter update**
   - What we know: D-18 specifies glow effect on active counter updates
   - What's unclear: Should glow persist briefly after update, or animate immediately?
   - Recommendation: Use Framer Motion `animate` prop with scale bump (1.0 → 1.02 → 1.0) plus glow class that persists for 300ms (per DESIGN.md "Short" duration)

## Environment Availability

> Skip condition: Phase 2 uses existing frontend dependencies (no new external tools required).

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Next.js dev server | ✓ | (system) | — |
| npm | Package management | ✓ | (system) | — |
| Framer Motion | Exit animations | ✓ | 12.38.0 | — |
| Tailwind CSS | Styling | ✓ | 4.x | — |

**Missing dependencies with no fallback:** None

**Missing dependencies with fallback:** None

## Validation Architecture

> Workflow nyquist_validation is set to false in config.json. Skipping this section.

## Sources

### Primary (HIGH confidence)
- [Framer Motion AnimatePresence Docs](https://motion.dev/docs/react-animate-presence) - Exit animation patterns, `mode="popLayout"`
- [CSS-Tricks repeating-linear-gradient](https://css-tricks.com/almanac/functions/r/repeating-linear-gradient/) - CSS pattern syntax
- [MDN Ordering Flex Items](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Ordering_flex_items) - `column-reverse` documentation

### Secondary (MEDIUM confidence)
- [CSS-Tricks Stripes in CSS](https://css-tricks.com/stripes-css/) - Iron bar overlay technique
- [CSS-Tricks Neon Text](https://css-tricks.com/how-to-create-neon-text-with-css/) - Glow effect implementation

### Tertiary (LOW confidence)
- None — all techniques verified with official docs or CSS-Tricks

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All libraries already installed and version-verified
- Architecture: HIGH — CSS gradient patterns are well-documented; Framer Motion exit animations are standard
- Pitfalls: HIGH — Common React/Framer Motion mistakes identified with clear solutions

**Research date:** 2026-03-25
**Valid until:** 90 days — CSS gradient patterns stable; Framer Motion API stable across v12.x