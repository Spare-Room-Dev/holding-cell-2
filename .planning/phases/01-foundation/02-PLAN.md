---
phase: 01-foundation
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - frontend/package.json
  - frontend/tsconfig.json
  - frontend/tailwind.config.ts
  - frontend/postcss.config.mjs
  - frontend/src/app/globals.css
  - frontend/src/app/layout.tsx
  - frontend/src/types/attack.ts
  - frontend/next.config.ts
autonomous: true
requirements:
  - FE-01
  - FE-02
  - FE-03
  - FE-04
  - FE-05
  - FE-06
  - DEV-05
must_haves:
  truths:
    - "Next.js app runs on port 3000"
    - "TypeScript is configured"
    - "Tailwind CSS is configured"
    - "Design tokens from DESIGN.md are defined in Tailwind config"
    - "IBM Plex Mono font is loaded"
    - "Satoshi and DM Sans fonts are loaded"
    - "Dark mode is the default theme"
    - "AttackEvent TypeScript interface matches backend Pydantic model"
  artifacts:
    - path: "frontend/package.json"
      provides: "Node dependencies"
      contains: "next"
      contains: "react"
      contains: "framer-motion"
      contains: "socket.io-client"
      contains: "tailwindcss"
    - path: "frontend/tailwind.config.ts"
      provides: "Tailwind configuration with DESIGN.md tokens"
      contains: "phosphor"
      contains: "darkMode"
      contains: "IBM Plex Mono"
    - path: "frontend/src/app/globals.css"
      provides: "Global styles with font imports"
      contains: "@import"
      contains: "IBM Plex Mono"
    - path: "frontend/src/types/attack.ts"
      provides: "TypeScript AttackEvent interface"
      exports: ["AttackEvent", "Archetype"]
    - path: "frontend/src/app/layout.tsx"
      provides: "Root layout with dark mode default"
      contains: "dark"
  key_links:
    - from: "frontend/tailwind.config.ts"
      to: "DESIGN.md"
      via: "color tokens and font families"
    - from: "frontend/src/types/attack.ts"
      to: "backend/models.py"
      via: "must match AttackEvent fields (keep in sync manually)"
---

<objective>
Create Next.js 14 frontend with TypeScript, Tailwind CSS, and design tokens from DESIGN.md. Establish the foundational styling and type definitions for the dashboard.

Purpose: Set up frontend scaffolding with proper theming and type safety.
Output: Running Next.js dev server on port 3000 with dark mode default and design tokens configured.
</objective>

<execution_context>
@/Users/rob/Documents/OT Apps/Holding Cell 2/.claude/get-shit-done/workflows/execute-plan.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/PROJECT.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/ROADMAP.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/STATE.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/phases/01-foundation/01-CONTEXT.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/phases/01-foundation/01-RESEARCH.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/PLAN.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/DESIGN.md

<interfaces>
<!-- Key contracts from DESIGN.md and backend types. -->

From DESIGN.md Color Tokens:
```typescript
// Primary accent colors
phosphor: {
  DEFAULT: '#00FF88',
  dim: '#00CC6A',
  glow: 'rgba(0, 255, 136, 0.15)',
}

// Background and surface colors
background: '#0D0D0D'
surface: {
  DEFAULT: '#1A1A1A',
  raised: '#222222',
}
border: '#2A2A2A'
borderSubtle: '#1F1F1F'

// Secondary accent
amber: '#FFB800'

// Alert/danger
alert: '#FF3B5C'

// Text colors
textPrimary: '#F0F0F0'
textMuted: '#6B6B6B'
textSubtle: '#3D3D3D'
```

From DESIGN.md Typography:
```typescript
// Font families
fontFamily: {
  display: ['Satoshi', 'sans-serif'],
  body: ['DM Sans', 'sans-serif'],
  mono: ['IBM Plex Mono', 'monospace'],
}

// Font sizes (Tailwind scale)
fontSize: {
  'display': ['48px', { lineHeight: '1.1', fontWeight: '900' }],
  'h1': ['24px', { lineHeight: '1.2', fontWeight: '700' }],
  'h2': ['18px', { lineHeight: '1.3', fontWeight: '700' }],
  'body': ['15px', { lineHeight: '1.5', fontWeight: '400' }],
  'label': ['13px', { lineHeight: '1.4', fontWeight: '400' }],
  'small': ['12px', { lineHeight: '1.4', fontWeight: '400' }],
  'caption': ['11px', { lineHeight: '1.3', fontWeight: '400' }],
  'mono': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
  'mono-sm': ['11px', { lineHeight: '1.4', fontWeight: '400' }],
}
```

From DESIGN.md Spacing:
```typescript
// Base unit: 8px
spacing: {
  '2xs': '2px',
  'xs': '4px',
  'sm': '8px',
  'md': '16px',
  'lg': '24px',
  'xl': '32px',
  '2xl': '48px',
  '3xl': '64px',
}
```

From PLAN.md AttackEvent (must match backend/models.py):
```typescript
interface AttackEvent {
  id: string;              // UUID
  timestamp: string;       // ISO 8601
  ip: string;              // "203.0.113.42"
  country: string;         // "Australia"
  countryCode: string;     // "AU"
  port: number;            // 22
  protocol: string;        // "SSH"
  archetype: Archetype;    // behavioral classification
  commands: string[];      // commands attempted
  duration: number;        // seconds
  rawLog: string;          // original fake log line
}

type Archetype =
  | "script_kiddie"
  | "botnet_drone"
  | "apt_operative"
  | "iot_worm"
  | "hacktivist";
```

From RESEARCH.md Tailwind Dark Mode:
```typescript
// tailwind.config.ts
darkMode: 'class'
// Default to dark via localStorage check in useEffect
// document.documentElement.classList.add('dark')
```

From RESEARCH.md Standard Stack Versions:
- Next.js: 16.2.1 (latest)
- React: 19
- Framer Motion: 12.38.0
- Socket.io-client: 4.8.3
- Tailwind CSS: 4.2.2
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Next.js app with TypeScript and Tailwind</name>
  <files>frontend/package.json, frontend/tsconfig.json, frontend/next.config.ts, frontend/postcss.config.mjs</files>
  <read_first>
    - This is a greenfield project (no existing files)
  </read_first>
  <action>Create frontend directory and initialize Next.js 14+ App Router with TypeScript and Tailwind CSS.

1. Run: `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir=false --import-alias="@/*" --use-npm`

2. Update frontend/package.json to include exact versions:
   - "next": "16.2.1" or latest stable
   - "react": "19" or latest
   - "react-dom": "19"
   - "framer-motion": "12.38.0" (per FE-02)
   - "socket.io-client": "4.8.3" (per FE-03)
   - "tailwindcss": "4.2.2"

3. Ensure tsconfig.json has:
   - "strict": true
   - "noEmit": true (Next.js handles compilation)
   - Paths: "@/*": ["./src/*"]

Per FE-01: Next.js 14+ App Router with TypeScript and Tailwind CSS.
Per DEV-05: frontend/package.json lists all Node dependencies.</action>
  <verify>
    <automated>test -f frontend/package.json && grep -q '"next"' frontend/package.json && grep -q '"framer-motion"' frontend/package.json && grep -q '"socket.io-client"' frontend/package.json</automated>
  </verify>
  <done>frontend/package.json exists with Next.js, TypeScript, Tailwind, Framer Motion, and Socket.io-client dependencies.</done>
</task>

<task type="auto">
  <name>Task 2: Configure Tailwind with DESIGN.md tokens</name>
  <files>frontend/tailwind.config.ts</files>
  <read_first>
    - DESIGN.md (for exact color values, typography, and spacing)
  </read_first>
  <action>Create frontend/tailwind.config.ts with complete design system:

1. Dark mode configuration (per FE-05):
   ```typescript
   darkMode: 'class'
   ```

2. Extend theme with colors from DESIGN.md:
   ```typescript
   colors: {
     phosphor: {
       DEFAULT: '#00FF88',
       dim: '#00CC6A',
       glow: 'rgba(0, 255, 136, 0.15)',
     },
     surface: {
       DEFAULT: '#1A1A1A',
       raised: '#222222',
     },
     background: '#0D0D0D',
     border: '#2A2A2A',
     'border-subtle': '#1F1F1F',
     amber: '#FFB800',
     alert: '#FF3B5C',
     'text-primary': '#F0F0F0',
     'text-muted': '#6B6B6B',
     'text-subtle': '#3D3D3D',
   }
   ```

3. Extend fontFamily:
   ```typescript
   fontFamily: {
     display: ['Satoshi', 'sans-serif'],
     body: ['DM Sans', 'sans-serif'],
     mono: ['IBM Plex Mono', 'monospace'],
   }
   ```

4. Extend fontSize with design system scale.

5. Extend spacing with 8px base unit scale.

Per FE-04: Design tokens from DESIGN.md (colors, typography, spacing).
Per FE-06: IBM Plex Mono for IPs, timestamps, attack types (tabular-nums).</action>
  <verify>
    <automated>grep -q "darkMode" frontend/tailwind.config.ts && grep -q "phosphor" frontend/tailwind.config.ts && grep -q "IBM Plex Mono" frontend/tailwind.config.ts && grep -q "Satoshi" frontend/tailwind.config.ts</automated>
  </verify>
  <done>frontend/tailwind.config.ts exists with all DESIGN.md tokens (colors, fonts, spacing) and dark mode 'class' configuration.</done>
</task>

<task type="auto">
  <name>Task 3: Configure global styles with font imports</name>
  <files>frontend/src/app/globals.css</files>
  <read_first>
    - DESIGN.md Typography section for font loading requirements
  </read_first>
  <action>Update frontend/src/app/globals.css:

1. Import fonts (per DESIGN.md):
   - Satoshi via Fontshare CDN: `@import url('https://api.fontshare.com/v2/css?f[]=satoshi@900,700&display=swap');`
   - DM Sans via Google Fonts: Add to layout.tsx next/font/google
   - IBM Plex Mono via Google Fonts: Add to layout.tsx next/font/google

2. Set CSS custom properties for colors:
   ```css
   :root {
     --color-phosphor: #00FF88;
     --color-phosphor-dim: #00CC6A;
     --color-phosphor-glow: rgba(0, 255, 136, 0.15);
     /* ... other tokens
   }
   ```

3. Dark mode default (per FE-05):
   ```css
   :root {
     color-scheme: dark;
   }

   html {
     color-scheme: dark;
   }
   ```

4. Base styles:
   ```css
   body {
     background-color: #0D0D0D;
     color: #F0F0F0;
     font-family: 'DM Sans', sans-serif;
   }

   .font-mono {
     font-variant-numeric: tabular-nums;
   }
   ```

5. Ensure Tailwind base directives are present:
   ```css
   @import "tailwindcss";
   ```

Per FE-06: tabular-nums for monospace numeric alignment.</action>
  <verify>
    <automated>grep -q "tabular-nums" frontend/src/app/globals.css && grep -q "color-scheme" frontend/src/app/globals.css</automated>
  </verify>
  <done>frontend/src/app/globals.css exists with font imports, color scheme (dark default), and tabular-nums for mono fonts.</done>
</task>

<task type="auto">
  <name>Task 4: Create root layout with dark mode and fonts</name>
  <files>frontend/src/app/layout.tsx</files>
  <read_first>
    - DESIGN.md Typography for font families
  </read_first>
  <action>Create frontend/src/app/layout.tsx:

1. Use next/font for DM Sans and IBM Plex Mono:
   ```typescript
   import { DM_Sans, IBM_Plex_Mono } from 'next/font/google'

   const dmSans = DM_Sans({
     subsets: ['latin'],
     variable: '--font-body',
   })

   const ibmPlexMono = IBM_Plex_Mono({
     subsets: ['latin'],
     weight: '400',
     variable: '--font-mono',
   })
   ```

2. Apply fonts to body:
   ```typescript
   <body className={`${dmSans.variable} ${ibmPlexMono.variable} font-body bg-background text-text-primary`}>
   ```

3. Set dark mode default via className on html:
   ```typescript
   <html lang="en" className="dark">
   ```

4. Include metadata for the app:
   ```typescript
   export const metadata: Metadata = {
     title: 'The Holding Cell',
     description: 'Real-time honeypot attack visualization',
   }
   ```

5. Import globals.css.

Per FE-05: Dark mode primary by default.
Per FE-06: IBM Plex Mono for IPs, timestamps, attack types.</action>
  <verify>
    <automated>grep -q "dark" frontend/src/app/layout.tsx && grep -q "IBM_Plex_Mono" frontend/src/app/layout.tsx && grep -q "DM_Sans" frontend/src/app/layout.tsx</automated>
  </verify>
  <done>frontend/src/app/layout.tsx exists with DM Sans and IBM Plex Mono fonts loaded, dark mode default, and proper metadata.</done>
</task>

<task type="auto">
  <name>Task 5: Create AttackEvent TypeScript interface</name>
  <files>frontend/src/types/attack.ts</files>
  <read_first>
    - PLAN.md Data Model section for AttackEvent structure
    - Must match backend/models.py exactly
  </read_first>
  <action>Create frontend/src/types/attack.ts with TypeScript definitions matching backend Pydantic model:

```typescript
// frontend/src/types/attack.ts

export type Archetype =
  | 'script_kiddie'
  | 'botnet_drone'
  | 'apt_operative'
  | 'iot_worm'
  | 'hacktivist';

export interface AttackEvent {
  id: string;              // UUID
  timestamp: string;       // ISO 8601
  ip: string;              // e.g., "203.0.113.42"
  country: string;         // e.g., "China"
  countryCode: string;     // e.g., "CN"
  port: number;            // e.g., 22
  protocol: string;        // e.g., "SSH"
  archetype: Archetype;    // behavioral classification
  commands: string[];      // commands attempted
  duration: number;        // seconds
  rawLog: string;          // original fake log line
}
```

Per D-10 to D-13: AttackEvent type defined separately in each codebase. Keep in sync manually with backend/models.py.

This interface will be used by:
- Socket.io client for type-safe event handling
- SocketContext for state management
- Dashboard components for rendering</action>
  <verify>
    <automated>grep -q "export type Archetype" frontend/src/types/attack.ts && grep -q "export interface AttackEvent" frontend/src/types/attack.ts && grep -q "archetype: Archetype" frontend/src/types/attack.ts</automated>
  </verify>
  <done>frontend/src/types/attack.ts exists with Archetype type and AttackEvent interface matching backend Pydantic model.</done>
</task>

</tasks>

<verification>
## Frontend Verification Commands

1. **Install dependencies:**
   ```bash
   cd frontend && npm install
   ```

2. **Start frontend dev server:**
   ```bash
   cd frontend && npm run dev
   ```

3. **Verify frontend running:**
   - Frontend starts on port 3000
   - http://localhost:3000 loads without errors
   - Browser console shows no font loading errors
   - Dark mode is active by default

4. **Verify Tailwind configuration:**
   - Custom colors are available (phosphor, surface, amber, etc.)
   - Custom fonts are loaded (Satoshi, DM Sans, IBM Plex Mono)
   - Font utility classes work (font-body, font-mono)
</verification>

<success_criteria>
- [ ] Next.js app runs on port 3000
- [ ] TypeScript strict mode enabled
- [ ] Tailwind CSS configured with DESIGN.md tokens
- [ ] Dark mode is default (html has 'dark' class)
- [ ] Phosphor green (#00FF88) is defined as primary color
- [ ] IBM Plex Mono font loaded and configured for tabular-nums
- [ ] DM Sans font loaded as body font
- [ ] Satoshi font loaded as display font
- [ ] AttackEvent TypeScript interface matches backend Pydantic model
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/02-SUMMARY.md`
</output>