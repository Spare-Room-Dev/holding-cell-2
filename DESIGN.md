# Design System — The Holding Cell

## Product Context
- **What this is:** The Holding Cell — a gamified SOC/threat intelligence visualization dashboard that renders honeypot attacks as pixel-art "bandits" being thrown into a jail cell.
- **Who it's for:** Recruiters evaluating a candidate's SOC operations, threat intelligence, and real-time data handling skills.
- **Space/industry:** Cybersecurity portfolio piece / threat intelligence visualization.
- **Project type:** Real-time dashboard (Next.js + FastAPI + Socket.io + Framer Motion).

## Aesthetic Direction
- **Direction:** Retro-Futuristic with light pixel-art accents — modern security operations dashboard with soul. Bloomberg Terminal meets Hyper Light Drifter. Not a retro game wearing a dashboard costume.
- **Decoration level:** Intentional — pixel-art accents exist but don't dominate. The prisoner avatars are the creative centerpiece. Stone/brick texture on the cell frame. Iron bar SVG overlay. Everything else is clean and professional.
- **Mood:** Competent enough to impress in a professional setting. Memorable enough to be unforgettable. Every design decision reinforces the "we made threat data feel like an arcade" concept without undermining credibility.
- **Reference sites:** N/A — this is a portfolio piece with a unique creative direction not found in category peers.

## Typography
- **Display/Hero:** Satoshi Bold 900 — geometric sans with character. Used for the main "HOLDING CELL" wordmark and section headers.
- **Body/UI:** DM Sans Regular 400 — humanist, readable, professional. Used for labels, buttons, nav, body copy.
- **UI/Labels:** Same as body.
- **Data/Tables:** IBM Plex Mono Regular 400 — warm monospace for IPs, timestamps, attack types, port numbers. Must support tabular-nums.
- **Code:** IBM Plex Mono Regular 400.
- **Loading:** Google Fonts (Satoshi via Fontshare CDN, DM Sans + IBM Plex Mono via Google Fonts).
- **Scale:**
  - Display: 48px / Satoshi Bold 900
  - H1: 24px / Satoshi Bold 700
  - H2: 18px / Satoshi Bold 700
  - Body: 15px / DM Sans Regular 400
  - Label: 13px / DM Sans Regular 400
  - Small: 12px / DM Sans Regular 400
  - Caption: 11px / DM Sans Regular 400
  - Mono: 14px / IBM Plex Mono Regular 400
  - Mono small: 11px / IBM Plex Mono Regular 400

## Color
- **Approach:** Restrained — three accent colors doing specific jobs. Not a rainbow. Not 8 shades of purple.
- **Background:** `#0D0D0D` — near-black, not harsh.
- **Surface:** `#1A1A1A` — card/panel backgrounds.
- **Surface Raised:** `#222222` — elevated components, sidebar.
- **Border:** `#2A2A2A` — default borders.
- **Border Subtle:** `#1F1F1F` — dividers within components.
- **Primary (Phosphor Green):** `#00FF88` — electric CRT phosphor. Used for: active states, live indicators, the "LIVE" badge, positive events, primary CTAs. Signature accent.
- **Primary Dim:** `#00CC6A` — hover state for primary.
- **Primary Glow:** `rgba(0, 255, 136, 0.15)` — glow/shadow effects.
- **Secondary (Amber):** `#FFB800` — CRT amber. Used for: medium-severity attacks, secondary highlights, hover states, warning-level threats.
- **Alert/Danger:** `#FF3B5C` — saturated red. Used for: critical attacks, error states, SQL injection labels.
- **Text Primary:** `#F0F0F0`
- **Text Muted:** `#6B6B6B`
- **Text Subtle:** `#3D3D3D`
- **Dark mode:** Dark is the primary theme. Light mode is available as a toggle but is not the primary design target. Light mode surfaces use `#F5F4F0` background, `#FFFFFF` surface, `#E0DDD5` borders, with the same accent colors desaturated ~15%.

## Spacing
- **Base unit:** 8px.
- **Density:** Comfortable — not cramped (corporate dashboard) and not cavernous (marketing site). Data-dense but breathable.
- **Scale:**
  - 2xs: 2px
  - xs: 4px
  - sm: 8px
  - md: 16px
  - lg: 24px
  - xl: 32px
  - 2xl: 48px
  - 3xl: 64px

## Layout
- **Approach:** Grid-disciplined shell with creative focal point. The app shell (header, stats row, sidebar) is clean and grid-disciplined — the "we can ship production UI" signal. The Jail Cell is the creative centerpiece — oversized, positioned prominently, animated.
- **Grid:** 12-column grid on desktop. Sidebar: 220px fixed. Main content: fluid.
- **Max content width:** 1200px.
- **Border radius:** Hierarchical scale — sm: 4px, md: 8px, lg: 12px, full: 9999px (pills/badges).

## Motion
- **Approach:** Intentional — every animation either aids comprehension or delivers the pixel-art theater. Not gratuitous.
- **Prisoner entrance:** Framer Motion physics — avatar flies in from above with spring easing, bounces slightly on landing. This is the core wow moment.
- **UI transitions:** Fade-slide entrances on stat cards (staggered 50ms between cards).
- **Live indicator:** Subtle glow pulse on the "LIVE" badge (1.5s ease-in-out infinite).
- **Hover states:** 150ms transitions on all interactive elements. Cards get a border-color shift on hover.
- **Easing:**
  - Enter: `ease-out`
  - Exit: `ease-in`
  - Move: `ease-in-out`
- **Duration:**
  - Micro: 50-100ms (hover states, toggles)
  - Short: 150-250ms (button states, card hovers)
  - Medium: 250-400ms (panel transitions, modal)
  - Long: 400-700ms (page entrances, prisoner animations)

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-24 | Initial design system created | Created by /design-consultation based on portfolio-first SOC dashboard concept |
| 2026-03-24 | Phosphor green (`#00FF88`) as primary accent | Retro terminal aesthetic without being heavy-handed. Used sparingly for maximum impact — live badge, active states, primary CTAs. |
| 2026-03-24 | Satoshi + DM Sans + IBM Plex Mono typography stack | Satoshi gives wordmark character; DM Sans is professional and readable; IBM Plex Mono brings warmth to data without being cold. |
| 2026-03-24 | Iron bars + stone texture as cell decoration | CSS-based (not images), subtle, reinforces theme without dominating the UI. |
| 2026-03-24 | Pixel-art prisoners with colored bandanas | Each prisoner gets a distinct bandana color for visual variety as they stack. Sprites are inline SVG — no external image dependencies. |
