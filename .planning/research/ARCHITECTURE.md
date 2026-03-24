# Architecture Research

**Domain:** SOC / Threat Intelligence Visualization Dashboard
**Researched:** 2026-03-24
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐   ┌───────────────────┐   ┌────────────────────────┐ │
│  │  JailCellGrid   │   │    StatsPanel     │   │   Header/LiveBadge     │ │
│  │  (visualization)│   │  (counters/kpis)  │   │  (connection status)   │ │
│  └────────┬─────────┘   └─────────┬────────┘   └───────────┬────────────┘ │
│           │                       │                         │              │
│           └───────────────────────┼─────────────────────────┘              │
│                                   │ WebSocket (Socket.io client)           │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │ ws://host:port
                                    │
┌───────────────────────────────────┼─────────────────────────────────────────┐
│                    BACKEND (FastAPI + Socket.io)                            │
├───────────────────────────────────┼─────────────────────────────────────────┤
│  ┌────────────────────────────────┴─────────────────────────────────────┐  │
│  │                    SocketServer (event broadcaster)                   │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐   │
│  │              AttackSource (honeypot / fake generator)                │   │
│  │  - Cowrie honeypot log tailer (Weekend 2)                           │   │
│  │  - Fake attack generator (Weekend 1, Approach A)                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation | Notes |
|-----------|----------------|------------------------|-------|
| AttackSource | Generate or forward raw attack events | FakeGenerator (Weekend 1) or CowrieLogTailer (Weekend 2) | One source per honeypot service |
| SocketServer | Broadcast events to all connected clients | python-socketio async server | Handles room management, reconnection |
| JailCellGrid | Visualize attacker "prisoners" in jail cell | React component + Framer Motion | Receives events via WebSocket |
| StatsPanel | Aggregate counters (archetype tallies, totals) | React component + useReducer | Derived state from attack stream |
| Header/LiveBadge | Show connection status and system health | React component | Auto-reconnect with backoff |
| ArchetypeClassifier | Classify raw honeypot logs into attacker archetypes | Rule-based classifier (Weekend 1) | Heaviest logic deferred to Weekend 2 |

## Recommended Project Structure

```
holding-cell/
├── backend/
│   ├── main.py                    # FastAPI app + Socket.io server bootstrap
│   ├── socket_server.py           # Socket.io event handlers (separate for clarity)
│   ├── models.py                  # Pydantic models (AttackEvent, etc.)
│   ├── attack_source/
│   │   ├── base.py               # Abstract base for attack sources
│   │   ├── fake_generator.py     # Weekend 1: simulated attacks
│   │   └── cowrie_tailer.py       # Weekend 2: real Cowrie log parsing
│   ├── classifiers/
│   │   └── archetype.py          # Archetype classification rules
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Main dashboard page
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   │
│   │   ├── components/
│   │   │   ├── JailCellGrid.tsx  # Cell container + prisoner stacking
│   │   │   ├── Prisoner.tsx      # Individual avatar (animated)
│   │   │   ├── ArrestRecord.tsx  # Hover tooltip (IP, country, etc.)
│   │   │   ├── StatsPanel.tsx    # Counter display
│   │   │   ├── LiveBadge.tsx    # Connection status indicator
│   │   │   └── Header.tsx       # Top bar with branding + status
│   │   │
│   │   ├── lib/
│   │   │   ├── socket.ts         # Socket.io client (typed, with reconnect)
│   │   │   └── useAttackStream.ts # React hook: socket → component state
│   │   │
│   │   ├── hooks/
│   │   │   └── usePrisoners.ts   # Manages prisoner list (cap at 20, fade-out)
│   │   │
│   │   └── types/
│   │       └── attack.ts         # Shared AttackEvent type
│   │
│   ├── public/
│   │   └── sprites/              # Pixel art per archetype (SVG or PNG)
│   │       ├── script-kiddie.svg
│   │       ├── botnet-drone.svg
│   │       └── ...
│   │
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── honeypot/                      # (Weekend 2) Honeypot service configs
│   └── cowrie/
│       └── cowrie.cfg
│
└── README.md
```

### Structure Rationale

- **backend/attack_source/:** Attack sources are swappable. Approach A uses FakeGenerator; Weekend 2 introduces CowrieTailer. Both implement the same interface. This boundary prevents the socket server from knowing where events originate.
- **frontend/components/:** UI is component-per-visual-element. JailCellGrid is the root; Prisoner is a leaf. StatsPanel and Header are siblings at the shell level.
- **frontend/lib/:** Socket.io client is isolated here. The `useAttackStream` hook wraps it for React — keeps components declarative.
- **frontend/hooks/:** `usePrisoners` encapsulates the 20-prisoner cap and fade-out logic. Components should not manage this themselves.
- **honeypot/:** Cowrie runs as a separate service. The tailer reads its log file — no code coupling between honeypot and the visualization server.

## Architectural Patterns

### Pattern 1: Event-Driven Streaming (Server-Sent WebSocket)

**What:** Backend pushes events to all connected clients over a persistent WebSocket connection. No polling.

**When to use:** Real-time dashboards where updates are frequent and unpredictable (attack events). Traditional REST polling is too slow and creates connection overhead.

**Trade-offs:**
- Pro: Sub-second latency, works for any event frequency
- Pro: Server controls push cadence
- Con: Client must handle reconnection (use exponential backoff)
- Con: WebSocket connections are stateful — harder to scale horizontally (requires sticky sessions or a message broker like Redis)

**Example (Python, python-socketio):**
```python
import socketio

sio = socketio.AsyncServer(async_mode='asgi')

@sio.on('connect')
async def on_connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.on('disconnect')
async def on_disconnect(sid):
    print(f"Client disconnected: {sid}")

async def broadcast_attack(event: AttackEvent):
    await sio.emit('attack_event', event.model_dump())
```

### Pattern 2: Source Abstraction (Strategy Pattern for Data Sources)

**What:** Multiple attack sources (fake generator, Cowrie honeypot) implement a common interface. The socket server does not care which source is active.

**When to use:** When the data source will change (Weekend 1 fake -> Weekend 2 real honeypot). Avoids rewriting the server as sources evolve.

**Trade-offs:**
- Pro: Swapping sources is a config change, not a code rewrite
- Pro: Testing is easier — inject a mock source
- Con: Adds an abstraction layer; must keep interface stable

**Example:**
```python
from abc import ABC, abstractmethod

class AttackSource(ABC):
    @abstractmethod
    async def start(self, handler: Callable[[AttackEvent], None]) -> None:
        """Start emitting events via the handler callback."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass
```

### Pattern 3: Immutable Event Log with Derived State

**What:** Raw attack events are immutable facts. All UI state (prisoner list, counters) is derived from the event stream.

**When to use:** When replay, audit, or time-travel debugging is desired. Even for Approach A, treating events as immutable makes the architecture more robust as complexity grows.

**Trade-offs:**
- Pro: Clear data flow — events are the source of truth
- Pro: Derived state is stateless — can be recomputed from events
- Con: For high-volume streams, storing all events is memory-intensive (use a ring buffer or database for persistence)

## Data Flow

### Real-Time Attack Event Flow

```
[AttackSource] ──▶ [ArchetypeClassifier] ──▶ [AttackEvent (validated)]
                                                      │
                                                      │ socketio.emit('attack_event', payload)
                                                      ▼
                                            [SocketServer broadcast]
                                                      │
                                                      │ WebSocket
                                                      ▼
                                    ┌────────────────────────────────┐
                                    │       All Connected Clients     │
                                    └──────────────┬─────────────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                     [JailCellGrid]        [StatsPanel]         [Header]
                     (add prisoner)         (increment)      (update live badge)
```

### State Management

```
[Socket.io Event]
       │
       ▼
[useAttackStream hook] ──▶ [Events array (ring buffer, last 1000)]
       │                          │
       │ (derived)                │ (derived)
       ▼                          ▼
[usePrisoners hook] ◀──── Stats + Prisoner List
       │
       ▼
[React Components re-render]
```

### Key Data Flows

1. **Attack arrival:** AttackSource emits event -> SocketServer broadcasts -> `useAttackStream` receives -> `usePrisoners` appends (capped at 20) -> `JailCellGrid` renders new Prisoner with Framer Motion entrance animation
2. **Counter update:** Same event -> StatsPanel increments relevant archetype counter
3. **Connection recovery:** Client disconnects -> `socket.ts` auto-reconnects with backoff -> on reconnect, `useAttackStream` requests last-N events from server (if implemented) or simply resumes streaming

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k concurrent viewers | Single FastAPI + Socket.io instance is fine. No message broker needed. |
| 1k-10k concurrent viewers | Add Redis adapter for python-socketio. Horizontal Socket.io server scaling with sticky sessions. |
| 10k+ concurrent viewers | Consider separating the WebSocket tier from the event ingestion tier. A message queue (Kafka/RabbitMQ) sits between honeypot logs and the WebSocket servers. |

### Scaling Priorities

1. **First bottleneck: WebSocket connection limit.** A single Node.js/Socket.io process handles ~10k concurrent connections. FastAPI with python-socketio is similar. Add horizontal scaling + Redis before hitting this limit.
2. **Second bottleneck: Event broadcast fan-out.** At high attack volume or many viewers, broadcasting every event to every socket is O(n*m). Redis Pub/Sub distributes the load across multiple Socket.io instances.
3. **Third bottleneck: Persistence.** At very high attack volume, in-memory event buffer overflows. Move to a ring buffer database (TimescaleDB, SQLite with size limit) for the event log.

For this project (single-viewer portfolio piece, honeypot attack volume): current architecture is sufficient at least 100x over-provisioned.

## Anti-Patterns

### Anti-Pattern 1: Polling-Based Real-Time

**What people do:** Use `setInterval` on the frontend to poll a REST endpoint every 1-5 seconds for new attacks.

**Why it's wrong:** Creates artificial latency (up to N seconds per event), clutters logs with polling requests, and the REST endpoint becomes a bottleneck at higher scale.

**Do this instead:** WebSocket push from the server. If REST is required for browser compatibility, use Server-Sent Events (SSE) as a fallback.

### Anti-Pattern 2: Embedding Business Logic in Socket Handlers

**What people do:** Put archetype classification, IP geolocation lookups, and event transformation directly inside the Socket.io `emit` call.

**Why it's wrong:** Socket handlers become a dumping ground. Testing requires a full Socket.io server. Reusing logic (e.g., for a REST endpoint that returns historical data) becomes impossible.

**Do this instead:** Process events in the AttackSource or a dedicated pipeline stage before emitting. Socket.io should only serialize and transmit.

### Anti-Pattern 3: Storing Derived State as Source of Truth

**What people do:** Increment a `total_attacks` counter variable on the server and read it directly, instead of counting events.

**Why it's wrong:** Counters can drift. If a client disconnects mid-event, the counter may be incremented but the client never received it. Derived state is correct only if computed from the canonical event log.

**Do this instead:** All state is derived from the event log. Counters are computed by querying the log. This is especially important when implementing session replay or historical views.

### Anti-Pattern 4: No Reconnection Strategy

**What people do:** Establish a WebSocket connection once on page load, with no retry logic if it drops.

**Why it's wrong:** Network interruptions happen. The dashboard silently goes stale with no indication to the user.

**Do this instead:** Implement exponential backoff reconnection (1s, 2s, 4s, 8s, max 30s). Show a "SIGNAL LOST" / "RECONNECTING" status in the UI. PLAN.md has already addressed this with the 30s max backoff.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Cowrie Honeypot | File tailer reading Cowrie JSON logs | Cowrie outputs to `%(logdir)s/cowrie.json`. The tailer follows the file (handles log rotation). Runs as a background task in the Python server. |
| Shodan API | REST API via httpx (async HTTP client) | Deferred to Weekend 3. Rate limit is the primary concern — implement a cache (60s TTL) and a polling interval of at least 60s between requests per IP. |
| IP Geolocation | MaxMind GeoIP or ip-api.com (free tier) | ip-api.com has 45 req/min limit on free tier. Cache aggressively. MaxMind GeoLite2 is more reliable for production. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| AttackSource -> SocketServer | In-process callback or asyncio Queue | The source emits events; the server broadcasts. No network hop needed. |
| Frontend -> Backend | WebSocket (Socket.io protocol) | Socket.io adds reconnection, heartbeat, and rooms on top of raw WebSocket. |
| Frontend components -> Socket | React hook (`useAttackStream`) | Components never interact with socket directly. The hook manages subscription lifecycle. |

## Sources

- python-socketio async server patterns — official documentation (MEDIUM confidence)
- SOC dashboard architecture patterns — general knowledge from threat intelligence platform design (MEDIUM confidence)
- Cowrie honeypot log format and integration — Cowrie GitHub repository documentation (MEDIUM confidence)
- WebSocket scaling with Socket.io + Redis — Socket.io documentation (MEDIUM confidence)

---

*Architecture research for: SOC / Threat Intelligence Visualization Dashboard*
*Researched: 2026-03-24*
