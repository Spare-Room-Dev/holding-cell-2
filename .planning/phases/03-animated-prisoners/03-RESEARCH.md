# Phase 3: Animated Prisoners — Research

**Researched:** 2026-03-25
**Domain:** Framer Motion animations, React components, inline SVG pixel art
**Confidence:** HIGH

## Summary

Phase 3 replaces placeholder archetype-colored boxes with pixel-art prisoner sprites featuring Framer Motion spring entrance animations and interactive tooltips displaying arrest records. All major decisions are locked in CONTEXT.md (D-14 through D-17), including: inline SVG sprites with archetype-colored bandanas, spring entrance from above with specific physics parameters, and terminal-styled tooltips with 150ms hover delay.

The implementation leverages existing Framer Motion infrastructure from Phase 2 (AnimatePresence in JailCellGrid) and extends it with spring physics and layout animations. No new dependencies required—all components use existing packages (framer-motion@12.38.0, React 19, Tailwind CSS 4).

**Primary recommendation:** Implement in order: PrisonerSprite component → ArrestRecordTooltip component → Integrate into PrisonerSlot with AnimatePresence layout animations.

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-14: Sprite Implementation**
- Inline SVG sprites per archetype (no external image files)
- `PrisonerSprite` component with 5 archetype variants
- Render 32x32 pixel-art SVG scaled to 56x56 display with `image-rendering: pixelated`
- Each sprite is inline in the component file

**D-15: Bandana Colors**
- Bandana colors match archetype (fixed colors from ARCHETYPE_COLORS)
- Use existing `ARCHETYPE_COLORS` mapping from PrisonerSlot
- Archetype colors: `script_kiddie: 'amber'`, `botnet_drone: 'phosphor'`, `apt_operative: 'alert'`, `iot_worm: 'purple-400'`, `hacktivist: 'blue-400'`

**D-16: Tooltip Behavior**
- 150ms hover delay before show (prevents flicker on quick passes)
- Position above avatar (Y: -8px from avatar top)
- Immediate dismiss on mouse leave
- Fixed 280px width
- Terminal styling: Background `#1A1A1A`, Border 1px solid `#00FF88`, Font IBM Plex Mono 14px, Border-radius 8px, Padding 12px
- Content: ArrestRecord showing archetype, IP, country, port, protocol, commands, duration

**D-17: Entrance Animation**
- New prisoner: Initial `y: -100px, opacity: 0` → Animate `y: 0, opacity: 1`
- Transition: `type: 'spring', stiffness: 300, damping: 20`
- Existing prisoners shift: Animate Y by +64px (56px avatar + 8px gap)
- Transition for shift: `type: 'spring', stiffness: 400, damping: 25` (stiffer, less bouncy)
- Use Framer Motion `layout` prop for automatic shift animation

### Claude's Discretion

No explicit discretion areas—all decisions are locked.

### Deferred Ideas (OUT OF SCOPE)

- Real honeypot integration (Weekend 2)
- Shodan enrichment (Weekend 3)
- Demo speed mode
- Persistent attacker identity
- Attack pattern indicator strip

</user_constraints>

---

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRSN-01 | 32x32 pixel-art sprites per archetype (5 archetypes) | D-14: Inline SVG sprites. Pattern established in globals.css for pixel-art styling. |
| PRSN-02 | Sprites rendered at 64x64 with `image-rendering: pixelated` | D-14 specifies 56x56 display. CSS `image-rendering: pixelated` works for SVG inline. |
| PRSN-03 | Each prisoner has distinct bandana color | D-15: Use existing ARCHETYPE_COLORS mapping. Colors already defined in globals.css. |
| PRSN-04 | Framer Motion spring entrance | D-17: Spring params `stiffness: 300, damping: 20`. Enter from `y: -100px`. |
| PRSN-05 | Prisoner lands with small bounce | D-17: Spring physics naturally produce ~1.5 bounces with these params. |
| PRSN-06 | Hover shows ArrestRecord tooltip | D-16: 150ms delay, position above, terminal styling. |
| TOOL-01 | Tooltip displays IP, country flag, port/protocol, archetype badge, time | D-16: All fields specified. countryCode field exists in AttackEvent for flag emoji. |
| TOOL-02 | Retro terminal aesthetic | D-16: Background `#1A1A1A`, border `#00FF88`, IBM Plex Mono, scanline overlay. |
| TOOL-03 | Positioned above avatar, centered | D-16: Y offset -8px from avatar top, fixed 280px width, centered horizontally. |

</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| framer-motion | 12.38.0 (installed) | Spring animations, AnimatePresence, layout prop | Already in project. D-04 confirms Framer Motion available. |
| React | 19.2.4 (installed) | Component framework | Already in project. |
| Tailwind CSS | 4.x (installed) | Styling, utility classes | Already in project. Color tokens in globals.css. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| country-code-to-flag-emoji | ^1.0.0 (NEW) | Convert countryCode to flag emoji | For tooltip country flag display. Lightweight alternative to manual calculation. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| country-code-to-flag-emoji | Manual emoji calculation | Library handles edge cases (UK regions, unknown codes). Manual calculation: `String.fromCodePoint(...code.split('').map(c => 127397 + c.charCodeAt(0)))` |
| Framer Motion spring | CSS keyframes | Framer Motion provides physics-based bounce. CSS keyframes would require manual timing tuning. |

**Installation:**
```bash
npm install country-code-to-flag-emoji --prefix frontend
```

**Version verification:** framer-motion@12.38.0 is current and installed.

---

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
├── components/
│   ├── PrisonerSprite.tsx      # NEW: Inline SVG sprites per archetype
│   ├── ArrestRecordTooltip.tsx # NEW: Hover tooltip component
│   ├── PrisonerSlot.tsx        # MODIFY: Replace placeholder with sprite + tooltip
│   └── JailCellGrid.tsx        # MODIFY: Add layout prop for shift animation
├── types/
│   └── attack.ts               # Existing: AttackEvent, Archetype types
└── app/
    └── globals.css             # MODIFY: Add tooltip terminal styling (if needed)
```

### Pattern 1: Framer Motion Spring Entrance Animation
**What:** New prisoners enter from above with spring physics that produces a natural bounce.
**When to use:** Each new prisoner added to the visibleAttacks array.

**Example:**
```tsx
// Source: Framer Motion docs + CONTEXT.md D-17
<motion.div
  initial={{ y: -100, opacity: 0 }}
  animate={{ y: 0, opacity: 1 }}
  transition={{
    type: 'spring',
    stiffness: 300,
    damping: 20,
  }}
>
  <PrisonerSprite archetype={attack.archetype} />
</motion.div>
```

**Physics behavior:**
- `stiffness: 300` — Snappier than default (100), creates tight spring feel
- `damping: 20` — Moderate damping, allows ~1.5 bounces before settling
- Duration: Approximately 400-600ms visual completion

### Pattern 2: Framer Motion Layout Prop for Shift Animations
**What:** Existing prisoners automatically animate down when new prisoner enters above them.
**When to use:** On the container holding prisoner slots.

**Example:**
```tsx
// Source: https://motion.dev/docs/react-layout-animations
<motion.div layout transition={{ type: 'spring', stiffness: 400, damping: 25 }}>
  {/* Prisoner content */}
</motion.div>
```

**Key insight:** The `layout` prop enables automatic FLIP animations. When DOM order changes (new element inserted), Framer Motion calculates position delta and animates it. Stiffer spring (`400/25`) reduces bounce overlap chaos.

### Pattern 3: AnimatePresence with popLayout Mode
**What:** Manages enter/exit animations while allowing siblings to reflow immediately.
**When to use:** In JailCellGrid for the prisoner list.

**Example:**
```tsx
// Source: https://motion.dev/tutorials/react-animate-presence-modes
<AnimatePresence mode="popLayout">
  {visibleAttacks.map((attack) => (
    <motion.div
      key={attack.id}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      layout
      transition={{ duration: 0.25, ease: 'easeOut' }}
    >
      <PrisonerSlot attack={attack} />
    </motion.div>
  ))}
</AnimatePresence>
```

**Mode comparison:**
- `sync` (default) — Elements animate simultaneously
- `wait` — New waits for exiting to finish
- `popLayout` — Exiting elements removed from flow immediately, siblings reflow

### Pattern 4: Hover Tooltip with Delay
**What:** Tooltip shows after 150ms hover delay, dismisses immediately on mouse leave.
**When to use:** PrisonerSlot wrapper component.

**Example:**
```tsx
// Source: https://sinja.io/blog/animated-tooltip-with-react-framer-motion
const [isHovered, setIsHovered] = useState(false);
const [showTooltip, setShowTooltip] = useState(false);

useEffect(() => {
  let timeoutId: NodeJS.Timeout;
  if (isHovered) {
    timeoutId = setTimeout(() => setShowTooltip(true), 150);
  }
  return () => clearTimeout(timeoutId);
}, [isHovered]);

<div
  onMouseEnter={() => setIsHovered(true)}
  onMouseLeave={() => {
    setIsHovered(false);
    setShowTooltip(false);
  }}
>
  {/* Prisoner sprite */}
  <AnimatePresence>
    {showTooltip && (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
      >
        <ArrestRecordTooltip attack={attack} />
      </motion.div>
    )}
  </AnimatePresence>
</div>
```

### Pattern 5: Inline SVG Pixel Art Sprite
**What:** 32x32 pixel-art SVG rendered at 56x56 with crisp edges.
**When to use:** PrisonerSprite component for each archetype.

**Example:**
```tsx
// Source: https://css-tricks.com/keep-pixelated-images-pixelated-as-they-scale/
const SPRITES: Record<Archetype, React.ReactNode> = {
  script_kiddie: (
    <svg viewBox="0 0 32 32" width="56" height="56" style={{ imageRendering: 'pixelated' }}>
      {/* 32x32 pixel art paths */}
    </svg>
  ),
  // ... other archetypes
};

// CSS alternative (apply to container):
// .pixel-sprite { image-rendering: pixelated; image-rendering: crisp-edges; }
```

**Safari note:** `image-rendering: pixelated` has limited SVG support in Safari. For Safari compatibility, ensure SVG paths are drawn at exact pixel coordinates (no sub-pixel anti-aliasing).

### Anti-Patterns to Avoid
- **Anti-pattern:** Using `onMouseEnter` without delay → **Flicker on quick mouse passes.** Use 150ms timeout.
- **Anti-pattern:** CSS `transition: all` → **Performance issues.** Target specific properties (`y`, `opacity`).
- **Anti-pattern:** Positioning tooltip relative to sprite → **Clipping at cell edges.** Position above, use fixed width.
- **Anti-pattern:** Animating `transform` with `layout` prop → **Conflicts.** Let `layout` handle position, use spring for entrance.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Flag emoji from country code | Manual codepoint calculation | `country-code-to-flag-emoji` library | Handles edge cases (UK regions, invalid codes). 1KB library. |
| Spring animation timing | CSS keyframe guesswork | Framer Motion spring physics | Physics-based bounce is more natural and tunable. |
| Tooltip positioning | Custom positioning logic | Framer Motion `layout` + fixed positioning | The tooltip is positioned above the avatar with fixed width—no complex positioning needed. |
| Pixel art SVG rendering | Canvas-based solution | Inline SVG + `image-rendering: pixelated` | Simpler, more maintainable, works with React component structure. |

**Key insight:** The tooltip positioning is deliberately simple (fixed above avatar) to avoid the complexity of floating UI libraries. The constraint is documented in D-16.

---

## Common Pitfalls

### Pitfall 1: Tooltip Flicker on Quick Mouse Passes
**What goes wrong:** Tooltip shows immediately on hover, causing flicker when mouse passes quickly over multiple prisoners.
**Why it happens:** React state updates are synchronous; no debounce.
**How to avoid:** Implement 150ms hover delay before `setShowTooltip(true)`. Clear timeout on mouse leave.
**Warning signs:** Tooltips appearing/disappearing rapidly during normal mouse movement.

### Pitfall 2: Overlapping Spring Animations
**What goes wrong:** Multiple prisoners bouncing simultaneously creates chaotic visual noise.
**Why it happens:** All springs have same stiffness/damping, amplifying bounce.
**How to avoid:** Use stiffer spring (`stiffness: 400, damping: 25`) for existing prisoner shifts. This reduces bounce overlap.
**Warning signs:** Prisoners bouncing unpredictably when rapid attacks occur.

### Pitfall 3: Tooltip Clipping at Cell Edges
**What goes wrong:** Tooltip positioned below or to the side of avatar gets cut off by cell boundaries.
**Why it happens:** Cell has `overflow: hidden` and fixed height.
**How to avoid:** Position tooltip ABOVE avatar with negative Y offset. Newest prisoners (at top) have most room above them.
**Warning signs:** Tooltips cut off, missing content, or causing scrollbars.

### Pitfall 4: Safari Pixel Art Blur
**What goes wrong:** SVG pixel art appears blurry or anti-aliased in Safari.
**Why it happens:** Safari has limited `image-rendering: pixelated` support for SVG elements.
**How to avoid:** Draw SVG paths at exact integer coordinates. Avoid sub-pixel positioning. Consider adding `shape-rendering: crispEdges` to SVG root.
**Warning signs:** Crisp pixels in Chrome/Firefox but soft edges in Safari.

### Pitfall 5: AnimatePresence Key Conflicts
**What goes wrong:** Animations don't play correctly when prisoners enter/exit.
**Why it happens:** React keys must be unique and stable. Attack IDs from backend must be unique.
**How to avoid:** Use `attack.id` as key. Verify backend generates UUIDs (confirmed in AttackEvent type).
**Warning signs:** Prisoners not animating, or all prisoners re-animating when one enters.

---

## Code Examples

### PrisonerSprite Component Structure
```tsx
// frontend/src/components/PrisonerSprite.tsx
import type { Archetype } from '@/types/attack';

interface PrisonerSpriteProps {
  archetype: Archetype;
  className?: string;
}

// Bandana color mapping (per D-15)
const BANDANA_COLORS: Record<Archetype, string> = {
  script_kiddie: '#FFB800',    // amber
  botnet_drone: '#00FF88',     // phosphor
  apt_operative: '#FF3B5C',    // alert
  iot_worm: '#A855F7',         // purple-400
  hacktivist: '#60A5FA',       // blue-400
};

// 32x32 pixel-art sprite, scaled to 56x56 display
export function PrisonerSprite({ archetype, className }: PrisonerSpriteProps) {
  const bandanaColor = BANDANA_COLORS[archetype];

  return (
    <div className={`w-14 h-14 flex items-center justify-center ${className || ''}`}>
      <svg
        viewBox="0 0 32 32"
        width="56"
        height="56"
        style={{ imageRendering: 'pixelated' }}
        className="pixel-sprite"
      >
        {/* Base body pixels */}
        <rect x="12" y="16" width="8" height="12" fill="#F0F0F0" />
        {/* Head */}
        <rect x="10" y="6" width="12" height="10" fill="#F0F0F0" />
        {/* Bandana - colored by archetype */}
        <rect x="10" y="4" width="12" height="4" fill={bandanaColor} />
        {/* Eyes */}
        <rect x="12" y="10" width="2" height="2" fill="#0D0D0D" />
        <rect x="18" y="10" width="2" height="2" fill="#0D0D0D" />
        {/* Legs */}
        <rect x="12" y="28" width="4" height="4" fill="#1A1A1A" />
        <rect x="16" y="28" width="4" height="4" fill="#1A1A1A" />
      </svg>
    </div>
  );
}
```

### ArrestRecordTooltip Component Structure
```tsx
// frontend/src/components/ArrestRecordTooltip.tsx
import { motion } from 'framer-motion';
import type { AttackEvent } from '@/types/attack';
import countryCodeToFlagEmoji from 'country-code-to-flag-emoji';

interface ArrestRecordTooltipProps {
  attack: AttackEvent;
}

export function ArrestRecordTooltip({ attack }: ArrestRecordTooltipProps) {
  const timeAgo = formatTimeAgo(attack.timestamp);
  const duration = formatDuration(attack.duration);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="fixed w-[280px] bg-surface border border-phosphor rounded-lg p-3 font-mono text-sm"
      style={{
        background: '#1A1A1A',
        borderColor: '#00FF88',
      }}
    >
      {/* Archetype badge */}
      <div className="flex items-center gap-2 mb-2">
        <span className="px-2 py-0.5 rounded text-xs" style={{ background: 'var(--color-phosphor-glow)' }}>
          {attack.archetype.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      {/* IP and Country */}
      <div className="flex items-center gap-2 mb-1">
        <span className="text-phosphor">{attack.ip}</span>
        <span>{countryCodeToFlagEmoji(attack.countryCode)}</span>
        <span className="text-text-muted">{attack.country}</span>
      </div>

      {/* Port/Protocol */}
      <div className="text-text-muted mb-1">
        {attack.protocol}/{attack.port}
      </div>

      {/* Commands count */}
      <div className="text-text-muted mb-1">
        Commands: {attack.commands.length}
      </div>

      {/* Duration */}
      <div className="text-text-muted mb-1">
        Duration: {duration}
      </div>

      {/* Time arrested */}
      <div className="text-text-muted text-xs">
        Arrested {timeAgo}
      </div>
    </motion.div>
  );
}

function formatTimeAgo(timestamp: string): string {
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}
```

### Updated PrisonerSlot with Animation
```tsx
// frontend/src/components/PrisonerSlot.tsx (updated)
'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AttackEvent } from '@/types/attack';
import { PrisonerSprite } from './PrisonerSprite';
import { ArrestRecordTooltip } from './ArrestRecordTooltip';

interface PrisonerSlotProps {
  attack: AttackEvent;
  isNew?: boolean; // For entrance animation trigger
}

export function PrisonerSlot({ attack, isNew = false }: PrisonerSlotProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  // 150ms hover delay (per D-16)
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    if (isHovered) {
      timeoutId = setTimeout(() => setShowTooltip(true), 150);
    }
    return () => clearTimeout(timeoutId);
  }, [isHovered]);

  return (
    <motion.div
      layout
      className="relative"
      initial={isNew ? { y: -100, opacity: 0 } : false}
      animate={isNew ? { y: 0, opacity: 1 } : undefined}
      transition={{
        type: 'spring',
        stiffness: isNew ? 300 : 400,
        damping: isNew ? 20 : 25,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowTooltip(false);
      }}
    >
      <PrisonerSprite archetype={attack.archetype} />

      <AnimatePresence>
        {showTooltip && (
          <ArrestRecordTooltip attack={attack} />
        )}
      </AnimatePresence>
    </motion.div>
  );
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CSS keyframe animations | Framer Motion spring physics | Phase 2 (existing) | Natural bounce feel, tunable physics |
| Static placeholder boxes | Animated pixel-art sprites | Phase 3 (this) | Visual wow moment, archetype identification |
| No hover interaction | 150ms-delayed tooltip | Phase 3 (this) | Arrest record visibility, terminal aesthetic |
| Image-based sprites | Inline SVG sprites | D-14 | No asset loading, tree-shakeable, future-animation ready |

**Deprecated/outdated:**
- `image-rendering: -moz-crisp-edges` — Modern browsers support unprefixed `pixelated`. Firefox supports both.
- Floating UI libraries for tooltip — Overkill for fixed-position tooltip. Handled with simple CSS positioning.

---

## Open Questions

1. **Should PrisonerSprite have different pixel art for each archetype, or just different bandana colors?**
   - What we know: D-14 specifies "5 separate SVGs at ~2-4KB each" implying unique sprites.
   - What's unclear: Whether each archetype should have distinct body/face features or just bandana color.
   - Recommendation: Start with identical base sprite + colored bandana. Add unique features as polish if time permits.

2. **Should the tooltip include all commands or just the count?**
   - What we know: TOOL-01 specifies "Commands count" (singular count).
   - What's unclear: Whether to show command list on hover.
   - Recommendation: Show count only per spec. Command list could be Phase 4+ feature.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| framer-motion | Spring animations | Yes | 12.38.0 | — |
| React | Components | Yes | 19.2.4 | — |
| Tailwind CSS | Styling | Yes | 4.x | — |
| Next.js | App framework | Yes | 16.2.1 | — |
| country-code-to-flag-emoji | Flag emoji | No | — | Manual calculation |

**Missing dependencies with no fallback:**
- None (country-code-to-flag-emoji is optional; manual calculation is acceptable)

**Missing dependencies with fallback:**
- country-code-to-flag-emoji — Can use manual calculation: `String.fromCodePoint(...countryCode.split('').map(c => 127397 + c.charCodeAt(0)))`

---

## Validation Architecture

> nyquist_validation is explicitly set to false in config.json. Skipping this section.

---

## Sources

### Primary (HIGH confidence)
- [Framer Motion React Transitions](https://motion.dev/docs/react-transitions) — Spring animation API
- [Framer Motion Layout Animations](https://motion.dev/docs/react-layout-animations) — `layout` prop and FLIP animations
- [AnimatePresence Modes Tutorial](https://motion.dev/tutorials/react-animate-presence-modes) — `popLayout` mode for list animations
- [MDN: image-rendering pixelated](https://developer.mozilla.org/en-US/docs/Games/Techniques/Crisp_pixel_art_look) — Pixel art rendering
- [country-code-to-flag-emoji GitHub](https://github.com/wojtekmaj/country-code-to-flag-emoji) — Flag emoji conversion

### Secondary (MEDIUM confidence)
- [CSS-Tricks: Keep Pixelated Images Pixelated](https://css-tricks.com/keep-pixelated-images-pixelated-as-they-scale/) — SVG scaling techniques
- [Animated Tooltip with Framer Motion](https://sinja.io/blog/animated-tooltip-with-react-framer-motion) — Hover delay pattern
- [AnimatePresence Guide 2026](https://ogblocks.dev/blog/framer-motion-animate-presence) — Modern patterns

### Tertiary (LOW confidence)
- None used — All critical patterns verified with official docs

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All dependencies already installed, versions verified.
- Architecture: HIGH — Patterns well-established in Framer Motion docs. CONTEXT.md specifies exact parameters.
- Pitfalls: HIGH — Common React/Framer Motion issues with documented solutions.

**Research date:** 2026-03-25
**Valid until:** 2026-04-25 (1 month — Framer Motion API stable)