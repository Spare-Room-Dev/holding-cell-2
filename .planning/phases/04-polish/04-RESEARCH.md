# Phase 4: Polish - Research

**Researched:** 2026-03-25
**Domain:** Responsive Layout, Theme Toggle, Mobile UX, Demo Polish
**Confidence:** HIGH

## Summary

Phase 4 is a polish phase focused on making the dashboard responsive across breakpoints, implementing a light mode toggle, and verifying the existing archetype classification logic end-to-end. The core visualization (prisoners, animations, tooltips) is complete from Phase 3. This phase adds responsive breakpoints, mobile bottom sheet for stats, and light mode CSS custom properties.

**Primary recommendation:** Use Tailwind v4's built-in `md:` (768px) and `lg:` (1024px) breakpoints with Framer Motion's `AnimatePresence` for the bottom sheet. Implement light mode by adding a `:root.light` CSS rule set and toggling a class on `<html>`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Desktop layout (>=1024px): Current 70/30 sidebar remains unchanged
- **D-02:** Tablet/small desktop (768px-1023px): Stack stats below JailCellGrid (100% width each)
- **D-03:** Mobile (<768px): Full responsive with stats in bottom sheet overlay
- **D-04:** Below 320px: Minimum supported width — layout may break below this
- **D-05:** Stats hidden by default on mobile (<768px)
- **D-06:** "Stats" button in header opens bottom sheet overlay
- **D-07:** Bottom sheet uses slide-up animation with backdrop
- **D-08:** Tap outside or swipe down dismisses sheet
- **D-09:** Toggle button in header (next to connection status)
- **D-10:** Uses CSS custom properties for theme switching
- **D-11:** Light mode colors from DESIGN.md: background `#F5F4F0`, surface `#FFFFFF`, borders `#E0DDD5`, accents desaturated ~15%
- **D-12:** No localStorage persistence in Phase 4 — default to dark on each visit
- **D-13:** Verify empty state displays correctly
- **D-14:** Verify disconnect UX ("SIGNAL LOST" banner, LIVE badge behavior)
- **D-15:** Verify archetype classification produces correct archetypes per BACK-08 rules
- **D-16:** Manual testing verification — no automated tests in this phase
- **D-17:** Counters use `toLocaleString()` for comma formatting
- **D-18:** Counter display caps at 99,999+ — verify existing CounterBox implementation

### Claude's Discretion
- Exact breakpoint values (recommend Tailwind `md:` and `lg:` breakpoints)
- Animation timing for bottom sheet (recommend DESIGN.md motion timing: 250-400ms)
- Exact light mode toggle placement in header
- Whether to add `prefers-color-scheme` detection (recommend: no, stick with explicit toggle)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-01 | Dashboard responsive on desktop; no layout breaks at 1200px max-width | Tailwind v4 breakpoints, existing flex layout in `page.tsx` |
| REQ-02 | All 5 archetype classifications work correctly based on fingerprint rules | Backend `archetypes.py` has rules, frontend displays classification — need manual verification |
| REQ-03 | Dark mode primary active by default; light mode toggle functional | CSS custom properties pattern, `layout.tsx` sets `className="dark"` |
| REQ-04 | Numbers format with locale commas; display caps at 99,999+ | `CounterBox.tsx` already implements both (lines 11-13) |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Tailwind CSS | 4.x | Responsive utilities, breakpoints | Already in project, CSS-first config in `globals.css` |
| Framer Motion | 12.38.0 | Bottom sheet animation, AnimatePresence | Already in project, used for prisoner entrance animations |
| Next.js | 16.2.1 | App Router, SSR handling | Already in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| CSS Custom Properties | Native | Theme switching | Light/dark mode toggle |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Framer Motion bottom sheet | Custom CSS transitions | Framer Motion already installed, provides better gesture handling and physics |
| CSS-only theme toggle | `next-themes` package | Overkill for Phase 4 — explicit toggle without persistence is simpler |
| Custom breakpoints | Tailwind defaults | CONTEXT.md specifies 768px and 1024px which align with `md:` and `lg:` |

**Version verification:**
- Tailwind CSS: 4.2.2 (latest)
- Framer Motion: 12.38.0 (installed)
- Next.js: 16.2.1 (installed)

## Architecture Patterns

### Recommended Project Structure

```
frontend/src/
├── app/
│   ├── page.tsx           # Add responsive classes, stats button
│   ├── layout.tsx         # Theme toggle context setup
│   └── globals.css        # Add light mode custom properties
├── components/
│   ├── StatsPanel.tsx     # Extract to shared component
│   ├── StatsBottomSheet.tsx  # NEW: Mobile bottom sheet
│   ├── ThemeToggle.tsx    # NEW: Header theme toggle button
│   ├── CounterBox.tsx     # Verify formatting (already implemented)
│   ├── ConnectionStatus.tsx  # Add stats button for mobile
│   └── JailCellGrid.tsx   # No changes (responsive container)
└── context/
    └── SocketContext.tsx  # No changes
```

### Pattern 1: Responsive Layout with Tailwind v4 Breakpoints

**What:** Use Tailwind's built-in breakpoints to switch between 70/30 layout (desktop), stacked layout (tablet), and mobile layout.

**When to use:** All responsive layout changes in `page.tsx`.

**Example:**
```tsx
// Source: Tailwind CSS v4 docs (https://tailwindcss.com/docs/breakpoints/)
// Default breakpoints: sm=640px, md=768px, lg=1024px, xl=1280px

// page.tsx responsive layout
<div className="p-lg h-[calc(100vh-5rem)]">
  <div className="flex flex-col lg:flex-row gap-md h-full">
    {/* Jail Cell - 70% width on desktop, 100% on tablet/mobile */}
    <div className="flex-[7] h-full lg:h-full min-h-[40vh] lg:min-h-0">
      <JailCellGrid />
    </div>
    {/* Stats Panel - 30% on desktop, hidden on mobile */}
    <div className="hidden lg:flex flex-[3] h-full overflow-y-auto bg-surface rounded-lg border border-border p-md">
      <StatsPanel />
    </div>
  </div>
</div>

{/* Mobile stats button in header */}
<button className="lg:hidden">
  <StatsIcon />
</button>
```

**Tailwind v4 breakpoint mapping:**
- `md:` = 768px and above (tablet+)
- `lg:` = 1024px and above (desktop+)
- Default = mobile-first (no prefix)

### Pattern 2: Bottom Sheet with Framer Motion

**What:** A mobile bottom sheet component using `AnimatePresence` and `motion.div` for slide-up animation with backdrop.

**When to use:** Mobile stats display (<768px).

**Example:**
```tsx
// Source: Framer Motion patterns (https://dawoodkmasood.medium.com/creating-a-bottom-spring-using-framer-motion-for-react-4b4fa0d0a20)
// and GitHub discussions (https://github.com/motiondivision/motion/issues/804)

import { AnimatePresence, motion } from 'framer-motion';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export function BottomSheet({ isOpen, onClose, children }: BottomSheetProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />
          {/* Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            drag="y"
            dragConstraints={{ top: 0 }}
            dragElastic={0.2}
            onDragEnd={(_, { offset, velocity }) => {
              if (offset.y > 100 || velocity.y > 500) {
                onClose();
              }
            }}
            className="fixed bottom-0 left-0 right-0 bg-surface-raised rounded-t-lg border-t border-border z-50 max-h-[70vh] overflow-y-auto p-lg"
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

**Animation timing per DESIGN.md:** Medium transitions 250-400ms, spring physics for smooth feel.

### Pattern 3: Light/Dark Mode with CSS Custom Properties

**What:** Use CSS custom properties for theming. Dark is default, toggle adds/removes `.light` class on `<html>`.

**When to use:** Theme switching throughout the app.

**Example:**
```css
/* Source: Theme toggle patterns (https://jeffszuc.com/posts/articles/theme-toggle) */

/* globals.css - Add after existing :root block */

/* Light mode theme */
:root.light {
  --color-background: #F5F4F0;
  --color-surface: #FFFFFF;
  --color-surface-raised: #F8F7F4;
  --color-border: #E0DDD5;
  --color-border-subtle: #ECEAE5;

  /* Desaturated accents (~15%) */
  --color-phosphor: #00DD77;        /* Slightly muted */
  --color-phosphor-dim: #00B05A;
  --color-phosphor-glow: rgba(0, 221, 119, 0.15);

  --color-amber: #E5A600;           /* Muted amber */
  --color-alert: #E53550;          /* Muted red */

  --color-text-primary: #1A1A1A;
  --color-text-muted: #666666;
  --color-text-subtle: #999999;
}

/* Switch color-scheme for proper form controls */
:root.light {
  color-scheme: light;
}
```

**React toggle component:**
```tsx
// Simple state toggle (no localStorage per D-12)
export function ThemeToggle() {
  const [isDark, setIsDark] = useState(true); // Dark default

  useEffect(() => {
    document.documentElement.classList.toggle('light', !isDark);
  }, [isDark]);

  return (
    <button onClick={() => setIsDark(!isDark)}>
      {isDark ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}
```

### Anti-Patterns to Avoid
- **localStorage persistence:** Per D-12, no persistence — default to dark each visit
- **`prefers-color-scheme` detection:** Per CONTEXT.md discretion, stick with explicit toggle
- **New breakpoint values:** Use Tailwind defaults (md=768px, lg=1024px) — matches CONTEXT.md requirements
- **max-width media queries:** Use mobile-first approach with `md:` and `lg:` prefixes

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bottom sheet | Custom drag/animation logic | Framer Motion `AnimatePresence` + `drag` prop | Gesture handling, spring physics, accessibility built-in |
| Theme toggle state | React Context for theme | Simple `useState` + `useEffect` | No persistence needed, just toggle class |
| Responsive breakpoints | Custom media queries | Tailwind `md:`, `lg:` classes | Already in Tailwind v4, matches project conventions |
| Counter formatting | Custom number formatting | `toLocaleString()` (already in CounterBox) | Locale-aware, standard API |

**Key insight:** This is primarily a CSS and layout adjustment phase. The heavy lifting (prisoner animations, socket connection, empty state) is complete from previous phases. Focus on responsive classes and bottom sheet component.

## Common Pitfalls

### Pitfall 1: Incorrect Breakpoint Values
**What goes wrong:** Using `sm:` (640px) instead of `md:` (768px) for tablet/mobile boundary.
**Why it happens:** Tailwind defaults are close but not exact matches to CONTEXT.md specs.
**How to avoid:** Use `md:` for <768px mobile threshold, `lg:` for >=1024px desktop. Tailwind defaults align with requirements.
**Warning signs:** Stats panel shows at wrong viewport sizes, bottom sheet triggers incorrectly.

### Pitfall 2: Framer Motion AnimatePresence Not Wrapping Correctly
**What goes wrong:** Bottom sheet doesn't animate in/out, just appears/disappears.
**Why it happens:** `AnimatePresence` must be parent of conditional render, and component must have `key` or `initial/animate/exit` props.
**How to avoid:** Ensure `AnimatePresence` wraps the conditional render and each `motion.div` has all three animation states.
**Warning signs:** No animation on open/close, sheet appears instantly.

### Pitfall 3: Theme Toggle FOUC (Flash of Unstyled Content)
**What goes wrong:** Page flashes wrong theme on initial load.
**Why it happens:** React hydration happens after initial paint, theme class not set yet.
**How to avoid:** Start with dark mode in layout.tsx `className="dark"` — already implemented. Light mode toggle adds `.light` class alongside `.dark`.
**Warning signs:** White flash on load, wrong theme briefly visible.

### Pitfall 4: Bottom Sheet Not Dismissing on Backdrop Tap
**What goes wrong:** Backdrop click doesn't close the sheet.
**Why it happens:** Event propagation blocked or click handler missing on backdrop.
**How to avoid:** Add `onClick={onClose}` to backdrop `motion.div` and ensure it's inside `AnimatePresence`.
**Warning signs:** Backdrop appears but sheet stays open.

### Pitfall 5: Archetype Verification Not Matching Backend Rules
**What goes wrong:** Frontend displays archetype but backend rules don't match expectations.
**Why it happens:** BACK-08 rules in `archetypes.py` define duration/command count ranges that may differ from intuition.
**How to avoid:** Manual verification per D-15: Run backend, check console logs for classification patterns:
- `script_kiddie`: <2min, <10cmds, no recon
- `botnet_drone`: repeated password attempts
- `apt_operative`: >10min, >50cmds, recon commands
- `iot_worm`: buildroot/busybox/mips in commands
- `hacktivist`: anonymous/free/hack in username
**Warning signs:** Wrong archetype badge showing for expected attack patterns.

## Code Examples

### Responsive Layout Update (page.tsx)

```tsx
// Current 70/30 layout - needs responsive breakpoints
// Source: Current implementation + Tailwind v4 docs

export default function Dashboard() {
  const [isStatsOpen, setIsStatsOpen] = useState(false);

  return (
    <main className="min-h-screen bg-background text-text-primary">
      {/* Header with stats button for mobile */}
      <header className="flex items-center justify-between px-lg py-md border-b border-border">
        <h1 className="font-display text-h1 text-text-primary">
          Holding Cell
        </h1>
        <div className="flex items-center gap-2">
          <ConnectionStatus />
          <ThemeToggle />
          {/* Stats button - visible on mobile/tablet, hidden on desktop */}
          <button
            className="md:lg:hidden p-sm rounded-md bg-surface-raised border border-border"
            onClick={() => setIsStatsOpen(true)}
          >
            Stats
          </button>
        </div>
      </header>

      {/* Main content - responsive layout */}
      <div className="p-lg h-[calc(100vh-5rem)]">
        {/* Desktop: flex-row 70/30, Tablet/Mobile: flex-col stacked */}
        <div className="flex flex-col lg:flex-row gap-md h-full">
          {/* Jail Cell - 70% on desktop, full width on mobile/tablet */}
          <div className="flex-[7] h-full min-h-[50vh] lg:min-h-0">
            <JailCellGrid />
          </div>
          {/* Stats Panel - 30% on desktop, hidden on mobile */}
          <div className="hidden lg:flex flex-[3] h-full overflow-y-auto bg-surface rounded-lg border border-border p-md">
            <StatsPanel />
          </div>
        </div>
      </div>

      {/* Mobile bottom sheet */}
      <BottomSheet isOpen={isStatsOpen} onClose={() => setIsStatsOpen(false)}>
        <StatsPanel />
      </BottomSheet>
    </main>
  );
}
```

### Light Mode CSS Additions (globals.css)

```css
/* Add after existing :root block */

/* Light mode theme - activated by .light class on <html> */
:root.light {
  /* Per D-11: Light mode colors from DESIGN.md */
  --color-background: #F5F4F0;
  --color-surface: #FFFFFF;
  --color-surface-raised: #F8F7F4;
  --color-border: #E0DDD5;
  --color-border-subtle: #ECEAE5;

  /* Desaturated accents (~15%) */
  --color-phosphor: #00DD77;
  --color-phosphor-dim: #00B05A;
  --color-phosphor-glow: rgba(0, 221, 119, 0.15);

  --color-amber: #E5A600;
  --color-alert: #E53550;

  --color-text-primary: #1A1A1A;
  --color-text-muted: #666666;
  --color-text-subtle: #999999;

  color-scheme: light;
}

/* Ensure dark mode class is set by default */
html.dark {
  color-scheme: dark;
}
```

### Bottom Sheet Component (new file)

```tsx
// frontend/src/components/BottomSheet.tsx
'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { ReactNode } from 'react';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
}

export function BottomSheet({ isOpen, onClose, children }: BottomSheetProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop - dismisses on tap */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Sheet - slide up with spring animation */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.2}
            onDragEnd={(_, { offset, velocity }) => {
              // Close if dragged down significantly or with velocity
              if (offset.y > 100 || velocity.y > 500) {
                onClose();
              }
            }}
            className="fixed bottom-0 left-0 right-0 bg-surface-raised rounded-t-lg border-t border-border z-50 max-h-[70vh] overflow-y-auto p-lg"
            role="dialog"
            aria-modal="true"
          >
            {/* Drag handle */}
            <div className="w-12 h-1 bg-text-subtle rounded-full mx-auto mb-md" />
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

### Theme Toggle Component (new file)

```tsx
// frontend/src/components/ThemeToggle.tsx
'use client';

import { useState, useEffect } from 'react';

export function ThemeToggle() {
  // Dark mode is default per D-16 and existing layout.tsx
  const [isDark, setIsDark] = useState(true);

  // No localStorage persistence per D-12
  useEffect(() => {
    // Toggle .light class (dark is already set in layout.tsx)
    document.documentElement.classList.toggle('light', !isDark);
    // Ensure dark class is set when toggling back
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="p-sm rounded-md hover:bg-surface-raised transition-colors"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? (
        // Sun icon for light mode
        <svg className="w-5 h-5 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ) : (
        // Moon icon for dark mode
        <svg className="w-5 h-5 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      )}
    </button>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `tailwind.config.js` for breakpoints | CSS-first `@theme` in v4 | Tailwind v4 (2025) | Simpler config, no JS build step |
| Custom theme context | `next-themes` package | 2024+ | Handles SSR, FOUC prevention |
| CSS-only bottom sheet | Framer Motion gestures | Motion library standard | Better UX with physics-based drag |

**Deprecated/outdated:**
- `tailwind.config.ts` for custom breakpoints: Use `@theme` in CSS for Tailwind v4
- `max-width` media queries: Use mobile-first with `min-width` breakpoints (`md:`, `lg:`)

## Open Questions

1. **Should we use `@container` queries for the JailCellGrid?**
   - What we know: Tailwind v4 supports container queries
   - What's unclear: Whether the grid should respond to container or viewport
   - Recommendation: Use viewport breakpoints for Phase 4 (simpler, matches existing patterns)

2. **Should bottom sheet have snap points?**
   - What we know: Common pattern (Instagram, Twitter) has multiple snap positions
   - What's unclear: Whether stats panel needs preview/expanded states
   - Recommendation: Single snap for Phase 4 — full height with `max-h-[70vh]` is sufficient

## Environment Availability

This phase has no external dependencies beyond the existing frontend stack (Next.js, Tailwind CSS v4, Framer Motion). All required packages are installed.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Frontend build | ✓ | v20+ | — |
| npm | Package management | ✓ | 10+ | — |
| Next.js | SSR, routing | ✓ | 16.2.1 | — |
| Tailwind CSS | Responsive utilities | ✓ | 4.x | — |
| Framer Motion | Animations | ✓ | 12.38.0 | — |

**Missing dependencies with no fallback:** None

## Sources

### Primary (HIGH confidence)
- [Tailwind CSS v4 Breakpoints](https://tailwindcss.com/docs/breakpoints/) — Official docs for responsive utilities
- [Framer Motion AnimatePresence](https://github.com/motiondivision/motion/issues/804) — Bottom sheet patterns
- [DESIGN.md](/DESIGN.md) — Color tokens, motion timing, spacing scale
- [backend/archetypes.py](/backend/archetypes.py) — Archetype classification rules
- [frontend/src/app/globals.css](/frontend/src/app/globals.css) — Existing CSS custom properties

### Secondary (MEDIUM confidence)
- [Bottom Sheet with Framer Motion](https://dawoodkmasood.medium.com/creating-a-bottom-spring-using-framer-motion-for-react-4b4fa0d0a20) — Implementation patterns
- [Theme Toggle with CSS Variables](https://jeffszuc.com/posts/articles/theme-toggle) — React + CSS custom properties approach

### Tertiary (LOW confidence)
- None — all critical patterns verified from primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All packages already installed and verified
- Architecture: HIGH — Patterns align with existing codebase and Tailwind v4 conventions
- Pitfalls: HIGH — Common responsive/layout issues well-documented

**Research date:** 2026-03-25
**Valid until:** 30 days — Tailwind v4 and Framer Motion APIs stable