# Stack Research: SOC / Threat Intelligence Dashboard

**Domain:** Real-time security operations center (SOC) dashboard with WebSocket updates and gamified visualization
**Researched:** 2026-03-24
**Confidence:** MEDIUM

**Research Note:** Web search and external fetch tools were unavailable during this session. Version numbers below are based on training data (knowledge cutoff late 2024). Verify versions via `npm view <package> version` and `pip show <package>` before implementation. Expect minor version differences.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Next.js** | 14.x (App Router) | React framework, frontend | App Router is the 2024-2025 standard. Server components reduce client bundle. Good Socket.io client integration. |
| **React** | 18.x | UI library | Comes with Next.js 14. Concurrent features not needed but harmless. |
| **TypeScript** | 5.x | Type safety | Standard for new projects. Catches AttackEvent shape mismatches at compile time. |
| **Tailwind CSS** | 3.4.x | Utility CSS | Rapid iteration on the retro-futuristic aesthetic. DESIGN.md spacing/color tokens map well to Tailwind config. |
| **Framer Motion** | 11.x | Animation | The prison entrance animation (spring physics, bounce on landing) requires physics-based animation. CSS keyframes cannot replicate the organic feel. 11.x has improved server component support. |
| **Socket.io Client** | 4.x | Real-time WebSocket | Mature auto-reconnect, binary transport fallback, typed events. Better than raw WebSocket for this use case. |

### Backend Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.11+ | Language runtime | PLAN.md specifies 3.11+. 3.12 offers ~10% faster interpreter. Avoid 3.13 until libraries catch up. |
| **FastAPI** | 0.110.x | ASGI web framework | Native async, Pydantic v2 integration, OpenAPI auto-docs. Weekend 2 Cowrie integration is Python-native. |
| **python-socketio** | 5.x | Async WebSocket server | Full async support, compatible with uvicorn. 5.x dropped Python 3.7 support but PLAN.md requires 3.11+ anyway. |
| **uvicorn** | 0.27.x | ASGI server | Standard for FastAPI. Run with `--loop uvloop` for production. |
| **Pydantic** | 2.x | Data validation | AttackEvent model validation. FastAPI dependency. v2 has significant performance improvements over v1. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **httpx** | 0.27.x | Async HTTP client | Weekend 2 Shodan API integration. Sync requests are simpler but httpx async pairs with FastAPI. |
| **python-socketio[asyncio]** | 5.x | Async engine | Ensure asyncio engine is installed: `python-socketio[asyncio]`. Without it, falls back to threading. |
| **jose** / **python-jose** | 3.3.x | JWT handling | Only if session auth added later. Not needed for MVP. |

---

## Installation

### Frontend (Next.js)

```bash
cd frontend
npm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
npm install socket.io-client@4 framer-motion@11 clsx tailwind-merge
npm install -D @types/node
```

### Backend (Python)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install fastapi==0.110.0 uvicorn[standard]==0.27.0 python-socketio[asyncio]==5.11.0 httpx==0.27.0 pydantic==2.6.0
```

### Dual-stack Development

```bash
# Option 1: Two terminals
# Terminal 1: cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000
# Terminal 2: cd frontend && npm run dev

# Option 2: Root package.json scripts
npm install -D concurrently
```

**Root package.json scripts:**
```json
{
  "scripts": {
    "dev:backend": "cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\""
  }
}
```

---

## Alternatives Considered

| Category | Recommended | Alternative | When to Use Alternative |
|----------|-------------|-------------|------------------------|
| Real-time transport | Socket.io (client 4.x) | SSE (Server-Sent Events) | SSE is simpler for one-way server→client only. Socket.io preferred here because PLAN.md keeps door open for future client→server commands (e.g., demo speed control). |
| Animation library | Framer Motion 11.x | CSS keyframes / React Spring | CSS keyframes cannot do spring physics bounce. React Spring is lighter but Framer Motion's API is more ergonomic for complex sequences. |
| Backend framework | FastAPI | Flask + Socket.io | Flask is sync-only by default. FastAPI's native async pairs better with python-socketio's async engine. |
| WebSocket server | python-socketio 5.x | websockets (bare library) | websockets is lower-level. python-socketio adds rooms, auto-reconnect semantics, and fallback to polling. |
| CSS approach | Tailwind CSS | CSS Modules / Styled Components | Tailwind + DESIGN.md token system maps directly. CSS Modules are fine but require more manual work for dark mode. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Socket.io 3.x** | Async support is second-class. Forces thread-based event loop. python-socketio 5.x is the 2024-2025 standard for async Python WebSocket. | python-socketio 5.x with asyncio engine |
| **Next.js 13 (Pages Router)** | App Router is the current standard. Pages Router is maintenance mode. PLAN.md specifies Next.js 14. | Next.js 14 App Router |
| **Pydantic v1** | End of life. FastAPI 0.110+ requires v2. Breaking changes from v1 to v2 but well-documented. | Pydantic v2 |
| **Flask** | Sync-only by default. Cowrie integration is Python-native — FastAPI's async gives better performance with python-socketio. | FastAPI |
| **Raw WebSocket (native API)** | No auto-reconnect, no fallback to polling, no room semantics. Fine for trivial use; inadequate for SOC dashboard with connection resilience requirements. | Socket.io client 4.x |
| **Framer Motion 10** | v11 has better server component support and improved `useInView` behavior. | Framer Motion 11.x |
| **Tailwind CSS 2.x** | v3.4 has improved dark mode, container queries, and better performance. | Tailwind CSS 3.4.x |

---

## Stack Patterns by Variant

**If Weekend 2 Cowrie integration is added:**
- Add `cowrie-client` or direct SSH log parsing to `backend/attack_generator.py`
- No stack change needed — same FastAPI + python-socketio pipeline

**If Shodan enrichment is added (Weekend 3):**
- Add `GET /shodan/{ip}` endpoint to FastAPI
- Add `httpx` async calls with rate limiting (Shodan has 1 req/sec free tier)
- Consider caching responses in-memory (dict) for repeated IPs

**If multiple honeypots are aggregated (v2+):**
- Introduce a message queue (Redis pub/sub or Celery)
- FastAPI workers consume from queue and emit to Socket.io
- Current synchronous-in-process architecture will not scale beyond 3-4 honeypots

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Next.js 14.x | React 18.x | Comes bundled |
| Tailwind CSS 3.4.x | Next.js 14 | PostCSS config works out of the box |
| Framer Motion 11.x | React 18.x | Server component support improved in 11.x |
| python-socketio 5.x | uvicorn 0.27.x | Use `--loop uvloop` for best async performance |
| FastAPI 0.110.x | Pydantic 2.x | 0.110+ requires Pydantic v2 |
| httpx 0.27.x | Python 3.11+ | Async only in 0.27.x (sync deprecated) |

---

## Sources

**HIGH confidence (Context7 / official docs):**
- None available during this session. Web search and external fetch were denied.

**MEDIUM confidence (training data, verify before use):**
- FastAPI 0.110.x — last checked in training data (late 2024), verify with `pip show fastapi`
- python-socketio 5.x — last checked in training data (late 2024), verify with `pip show python-socketio`
- Next.js 14 App Router patterns — training data consistent with current docs
- Framer Motion 11.x — training data, verify with `npm show framer-motion`

**LOW confidence (training data only, needs validation):**
- Specific patch versions (0.110.0, 0.27.0, etc.) — single source, verify with `npm/pip view`
- Tailwind CSS 3.4.x exact version — training data from late 2024

---

## Verification Checklist

Before implementation, verify:

```bash
# Frontend versions
npm view next version
npm view framer-motion version
npm view socket.io-client version
npm view tailwindcss version

# Backend versions
pip show fastapi | grep Version
pip show python-socketio | grep Version
pip show uvicorn | grep Version
pip show httpx | grep Version
pip show pydantic | grep Version
```

Update this document with verified versions once confirmed.

---

*Stack research for: SOC / Threat Intelligence Dashboard*
*Researched: 2026-03-24*
