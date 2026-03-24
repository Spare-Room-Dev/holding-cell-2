# Project Research Summary

**Project:** The Holding Cell (SOC / Threat Intelligence Dashboard)
**Domain:** Real-time security operations center dashboard with gamified visualization
**Researched:** 2026-03-24
**Confidence:** MEDIUM

## Executive Summary

This is a portfolio-ready SOC dashboard that visualizes honeypot attacks as pixel-art prisoners in a jail cell. The core insight from research is that enterprise SOC tools (Splunk, QRadar, Sentinel) are powerful but visually boring -- memorability comes from the theatrical jail cell metaphor, not enterprise functionality. The recommended architecture uses Next.js 14 App Router for the frontend with Framer Motion for physics-based prisoner animations, paired with a FastAPI + python-socketio backend for real-time event streaming.

The key risk is premature scope expansion. The gamified visualization is the differentiator; adding enterprise features (multi-honeypot aggregation, full SIEM connectors, ML threat scoring) before the core experience works would dilute the portfolio value. Version numbers in the stack research are based on training data (web search was unavailable during research) and must be verified with `npm/pip view` before implementation.

## Key Findings

### Recommended Stack

**Frontend:** Next.js 14 (App Router) + React 18 + TypeScript 5 + Tailwind CSS 3.4 + Framer Motion 11 + Socket.io Client 4
**Backend:** Python 3.11+ + FastAPI 0.110 + python-socketio 5 (async) + uvicorn 0.27 + Pydantic 2
**Supporting:** httpx for async HTTP (Shodan integration in v1.x)

The App Router is the 2024-2025 standard; Server Components reduce client bundle. Framer Motion is required for the physics-based spring bounce animation on prisoner entrance -- CSS keyframes cannot replicate the organic feel. python-socketio 5 is the async standard; Socket.io 3.x forces thread-based event loop and must be avoided. FastAPI's native async pairs better with python-socketio's asyncio engine than Flask would.

### Expected Features

**Must have (table stakes):**
- Real-time attack feed via Socket.io -- core pipeline, everything depends on this
- Attack count statistics -- situational awareness in one second
- Geographic origin (country flags) -- attackers come from somewhere
- Connection status indicator -- "LIVE" badge with auto-reconnect
- Dark mode -- SOC analysts work in low-light; explicitly required by DESIGN.md

**Should have (differentiators):**
- Gamified jail cell visualization with pixel-art prisoners -- the "wow moment"
- Animated prisoner entrance with Framer Motion spring physics -- shows real-time data handling + animation competence
- Hover arrest record tooltip -- IP, country, protocol, archetype, timestamp on demand
- 5-archetype classification (script_kiddie, botnet_drone, apt_operative, iot_worm, hacktivist) -- educational and visually distinct
- Attack severity color coding -- amber for medium, red for critical

**Defer to v2+:**
- Real Cowrie honeypot integration (Weekend 2 per PLAN.md)
- Shodan IP enrichment (v1.x after core is validated)
- Multi-honeypot aggregation (T-Pot ecosystem)
- Geographic world map with animated attack paths
- ML-based threat scoring
- Export/reporting

### Architecture Approach

Event-driven streaming with WebSocket. The backend AttackSource emits events through an ArchetypeClassifier into validated AttackEvents, which the SocketServer broadcasts to all connected clients. Source abstraction (Strategy pattern) allows swapping FakeGenerator for CowrieLogTailer without code changes. Frontend components receive events via `useAttackStream` hook and derive all state from the event stream -- no client-side counters as source of truth.

**Major components:**
1. **AttackSource** -- generates or forwards raw attack events (FakeGenerator or CowrieLogTailer)
2. **SocketServer** -- broadcasts events to all connected clients (python-socketio async)
3. **JailCellGrid** -- renders prisoners with Framer Motion entrance animation
4. **StatsPanel** -- aggregates archetype counters from event stream
5. **LiveBadge** -- shows connection status with exponential backoff reconnection
6. **useAttackStream hook** -- isolates Socket.io client from components

### Critical Pitfalls

1. **No reconnection strategy** -- network interruptions happen. Implement exponential backoff (1s, 2s, 4s, 8s, max 30s) with "SIGNAL LOST" UI indicator.
2. **Embedding business logic in Socket handlers** -- classification and transformation belong in AttackSource pipeline, not in emit calls.
3. **Polling-based "real-time"** -- setInterval polling is wrong. Use WebSocket push.
4. **Storing derived state as source of truth** -- server counters drift; all state derives from immutable event log.
5. **Premature scope expansion** -- adding multi-honeypot or SIEM connectors before the core experience works dilutes portfolio value.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation (Backend + Real-Time Pipeline)
**Rationale:** The entire visualization depends on the Socket.io event pipeline. Nothing else works without this.
**Delivers:** FastAPI app with Socket.io server, FakeGenerator producing attack events, typed AttackEvent model with Pydantic 2, client connection with auto-reconnect.
**Avoids:** PITFALL: no reconnection strategy. Build reconnection from day one.

### Phase 2: Core Visualization (JailCellGrid + StatsPanel)
**Rationale:** The jail cell metaphor is the product. Stats provide situational awareness. These should land before animation work so the data flow is proven.
**Delivers:** JailCellGrid with 20-prisoner cap, StatsPanel with archetype counters, LiveBadge connection indicator, dark retro-futuristic aesthetic per DESIGN.md.
**Uses:** Framer Motion 11, Tailwind CSS 3.4 with DESIGN.md tokens.

### Phase 3: Animated Prisoner Experience
**Rationale:** The physics-based spring entrance animation is the "wow moment" that differentiates from every other SOC dashboard. It depends on Phase 2 having the static visualization working.
**Delivers:** Prisoner component with sprite per archetype, Framer Motion spring physics (bounce on landing), hover ArrestRecord tooltip.
**Avoids:** PITFALL: business logic in socket handlers. Animation data flows through the hook, not socket logic.

### Phase 4: Validation Polish
**Rationale:** MVP should ship with features that impress recruiters, not half-working experiments. This phase ensures everything is solid.
**Delivers:** Attack archetype classification (5 types) working end-to-end, responsive layout, 5-archetype sprite set, demo speed mode toggle.
**Addresses:** FEATURES.md P1 features -- this completes the MVP definition.

### Phase Ordering Rationale

- Phase 1 first: backend pipeline is the foundation; no visualization works without it
- Phase 2 before 3: static visualization should work before adding animation complexity
- Phase 3 wow moment: Framer Motion spring animation requires proven data flow first
- Phase 4 polish: MVP requires everything working, not everything attempted
- Shodan enrichment and Cowrie integration are Weekend 2+ scope per PLAN.md

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Animation):** Framer Motion 11 server component patterns -- verify API compatibility with Next.js 14 App Router. Training data suggests compatibility but not verified with Context7.
- **Phase 1 (Backend):** python-socketio async integration with FastAPI ASGI -- documented in training data, verify with official docs before implementing.

Phases with standard patterns (skip research-phase):
- **Phase 2 (StatsPanel, JailCellGrid):** React component patterns are well-documented. Socket.io client hook pattern is standard.
- **Phase 4 (Polishing):** Feature implementations are incremental improvements, not new patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Web search unavailable during research. Version numbers from training data (late 2024). Verify with `npm/pip view` before implementation. |
| Features | MEDIUM | Based on training data knowledge of SOC platforms (Splunk, QRadar, Sentinel) and honeypot systems (Cowrie, Dionaea). Competitor analysis via product docs not available during this session. |
| Architecture | MEDIUM | python-socketio async patterns from official docs (training data). Event-driven architecture is standard; no novel patterns introduced. |
| Pitfalls | MEDIUM | Anti-patterns identified from general knowledge and architecture best practices. PITFALLS.md was not provided in this research cycle -- flagged as gap below. |

**Overall confidence:** MEDIUM

### Gaps to Address

- **PITFALLS.md not provided:** No critical/moderate/minor pitfalls document was included in this research cycle. The anti-patterns listed above are derived from ARCHITECTURE.md's anti-patterns section, not a dedicated pitfalls analysis. During roadmap creation, a dedicated pitfalls review should be scheduled.
- **Version verification needed:** All specific package versions (0.110.0, 0.27.0, etc.) are single-source training data. Must run `npm view <package> version` and `pip show <package>` before implementation.
- **DESIGN.md integration:** DESIGN.md was referenced but not read during research. Confirm that Tailwind CSS 3.4 configuration aligns with DESIGN.md spacing and color tokens before Phase 2.
- **Framer Motion + Next.js 14 App Router:** Training data suggests Framer Motion 11 has improved server component support, but this has not been verified with Context7 or official Framer Motion docs.

## Sources

### Primary (HIGH confidence)
- None available -- web search and external fetch were unavailable during research session.

### Secondary (MEDIUM confidence)
- FastAPI 0.110.x -- training data (late 2024), verify with `pip show fastapi`
- python-socketio 5.x -- training data (late 2024), verify with `pip show python-socketio`
- Next.js 14 App Router patterns -- training data consistent with current docs
- Framer Motion 11.x -- training data, verify with `npm show framer-motion`
- SOC platform feature analysis (Splunk, QRadar, Sentinel) -- training data knowledge
- Cowrie honeypot integration patterns -- training data from Cowrie GitHub docs

### Tertiary (LOW confidence)
- Specific patch versions (0.110.0, 0.27.0, 5.11.0, etc.) -- single source, needs validation
- Tailwind CSS 3.4.x exact version -- training data from late 2024, verify
- ip-api.com rate limits and caching behavior -- unverified during research

---

*Research completed: 2026-03-24*
*Ready for roadmap: yes*
