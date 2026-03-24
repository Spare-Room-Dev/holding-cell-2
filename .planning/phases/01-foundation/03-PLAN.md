---
phase: 01-foundation
plan: 03
type: execute
wave: 2
depends_on: ["02"]
files_modified:
  - frontend/src/lib/socket.ts
  - frontend/src/context/SocketContext.tsx
  - frontend/src/components/ConnectionStatus.tsx
  - frontend/src/app/layout.tsx
  - frontend/src/app/page.tsx
autonomous: true
requirements:
  - RTCL-01
  - RTCL-02
  - RTCL-03
  - RTCL-04
  - RTCL-05
must_haves:
  truths:
    - "Socket.io client connects to ws://localhost:8000 on page load"
    - "Client auto-reconnects with exponential backoff (1s, 2s, 4s, max 30s) on disconnect"
    - "'SIGNAL LOST' banner displays on dashboard during disconnect"
    - "Connection state displays via 'LIVE' badge with phosphor green glow pulse"
    - "React Context provides connection status and attack array to components"
    - "Attack events received from socket are stored in context state"
  artifacts:
    - path: "frontend/src/lib/socket.ts"
      provides: "Socket.io client factory"
      exports: ["createSocket"]
      contains: "reconnectionDelay: 1000"
      contains: "reconnectionDelayMax: 30000"
    - path: "frontend/src/context/SocketContext.tsx"
      provides: "React Context for connection state and attacks"
      exports: ["SocketProvider", "useSocket"]
      contains: "useReducer"
      contains: "NEW_ATTACK"
    - path: "frontend/src/components/ConnectionStatus.tsx"
      provides: "LIVE badge and SIGNAL LOST banner"
      exports: ["ConnectionStatus"]
      contains: "SIGNAL LOST"
      contains: "LIVE"
    - path: "frontend/src/app/layout.tsx"
      provides: "Root layout with SocketProvider"
      contains: "SocketProvider"
    - path: "frontend/src/app/page.tsx"
      provides: "Dashboard page showing connection status"
      contains: "ConnectionStatus"
  key_links:
    - from: "frontend/src/lib/socket.ts"
      to: "ws://localhost:8000"
      via: "io() connection"
    - from: "frontend/src/context/SocketContext.tsx"
      to: "frontend/src/lib/socket.ts"
      via: "createSocket()"
    - from: "frontend/src/context/SocketContext.tsx"
      to: "frontend/src/types/attack.ts"
      via: "import AttackEvent"
    - from: "frontend/src/components/ConnectionStatus.tsx"
      to: "frontend/src/context/SocketContext.tsx"
      via: "useSocket()"
    - from: "frontend/src/app/layout.tsx"
      to: "frontend/src/context/SocketContext.tsx"
      via: "SocketProvider wrapper"
---

<objective>
Implement Socket.io client with React Context for connection state management, and create ConnectionStatus component showing LIVE badge (connected) or SIGNAL LOST banner (disconnected).

Purpose: Enable real-time WebSocket communication with backend and display connection status to user.
Output: Dashboard page that shows connection status in real-time with automatic reconnection.
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
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/phases/01-foundation/02-PLAN.md

<interfaces>
<!-- Key contracts from previous plans and RESEARCH.md. -->

From frontend/src/types/attack.ts (Plan 02):
```typescript
export type Archetype =
  | 'script_kiddie'
  | 'botnet_drone'
  | 'apt_operative'
  | 'iot_worm'
  | 'hacktivist';

export interface AttackEvent {
  id: string;
  timestamp: string;
  ip: string;
  country: string;
  countryCode: string;
  port: number;
  protocol: string;
  archetype: Archetype;
  commands: string[];
  duration: number;
  rawLog: string;
}
```

From frontend/tailwind.config.ts (Plan 02):
```typescript
// Available color classes
'bg-phosphor' // #00FF88
'bg-phosphor-dim' // #00CC6A
'text-phosphor'
'bg-surface' // #1A1A1A
'bg-surface-raised' // #222222
'bg-background' // #0D0D0D
'border-border' // #2A2A2A
'text-text-primary' // #F0F0F0
'text-text-muted' // #6B6B6B
'text-alert' // #FF3B5C
'text-amber' // #FFB800
```

From RESEARCH.md Pattern 2 (Socket.io Client with Exponential Backoff):
```typescript
// Per RTCL-02: exponential backoff (1s, 2s, 4s, max 30s)
const SOCKET_URL = 'ws://localhost:8000';

export const createSocket = (): Socket => {
  return io(SOCKET_URL, {
    reconnection: true,
    reconnectionDelay: 1000,      // Start at 1 second
    reconnectionDelayMax: 30000,  // Max 30 seconds
    randomizationFactor: 0.5,     // Add jitter
    transports: ['websocket'],    // WebSocket only for localhost
  });
};
```

From RESEARCH.md Pattern 3 (React Context for Connection State):
```typescript
// SocketContext.tsx
'use client';

type ConnectionStatus = 'connected' | 'disconnected' | 'reconnecting';

interface SocketState {
  status: ConnectionStatus;
  attacks: AttackEvent[];
}

type SocketAction =
  | { type: 'CONNECTED' }
  | { type: 'DISCONNECTED' }
  | { type: 'RECONNECTING' }
  | { type: 'NEW_ATTACK'; payload: AttackEvent };

// useReducer for state management
// useEffect for socket lifecycle
// Cleanup on unmount: socket.disconnect()
```

From DESIGN.md Motion:
- Live indicator: Subtle glow pulse on the "LIVE" badge (1.5s ease-in-out infinite)
- Duration: Medium: 250-400ms for panel transitions

From CONTEXT.md D-05:
- Reconnection: exponential backoff (1s, 2s, 4s, max 30s) per RTCL-02

From CONTEXT.md D-06:
- Events during disconnect are lost — acceptable for Approach A v1 (RTCL-05)

From CONTEXT.md D-14 to D-15:
- React Context + useReducer for connection state and received attacks
- Context provides: connection status, attacks array, connect/disconnect handlers
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Socket.io client with exponential backoff</name>
  <files>frontend/src/lib/socket.ts</files>
  <read_first>
    - RESEARCH.md Pattern 2 (Socket.io Client configuration)
    - CONTEXT.md D-05 (reconnection config)
    - CONTEXT.md D-06 (events during disconnect acceptable)
  </read_first>
  <action>Create frontend/src/lib/socket.ts:

```typescript
// frontend/src/lib/socket.ts
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = 'ws://localhost:8000';

/**
 * Creates a Socket.io client with exponential backoff reconnection.
 *
 * Reconnection sequence per RTCL-02:
 * - 1st attempt: ~1000ms (base)
 * - 2nd attempt: ~2000ms
 * - 3rd attempt: ~4000ms
 * - Subsequent: capped at 30000ms with jitter
 *
 * Note: Events emitted during disconnect are lost (acceptable for v1 per RTCL-05).
 */
export const createSocket = (): Socket => {
  return io(SOCKET_URL, {
    reconnection: true,
    reconnectionDelay: 1000,      // Start at 1 second
    reconnectionDelayMax: 30000,  // Max 30 seconds
    randomizationFactor: 0.5,     // Add jitter for backoff
    transports: ['websocket'],    // WebSocket only (no polling for localhost)
  });
};
```

Per RTCL-01: Socket.io client connects to ws://localhost:8000 on page load.
Per RTCL-02: Client auto-reconnects with exponential backoff (1s, 2s, 4s, max 30s).
Per RTCL-05: Events emitted during disconnect are lost — acceptable for v1.</action>
  <verify>
    <automated>grep -q "reconnectionDelay: 1000" frontend/src/lib/socket.ts && grep -q "reconnectionDelayMax: 30000" frontend/src/lib/socket.ts && grep -q "ws://localhost:8000" frontend/src/lib/socket.ts</automated>
  </verify>
  <done>frontend/src/lib/socket.ts exists with createSocket() function configured for exponential backoff reconnection.</done>
</task>

<task type="auto">
  <name>Task 2: Create SocketContext for connection state</name>
  <files>frontend/src/context/SocketContext.tsx</files>
  <read_first>
    - frontend/src/lib/socket.ts (for createSocket import)
    - frontend/src/types/attack.ts (for AttackEvent import)
    - RESEARCH.md Pattern 3 (React Context pattern)
    - CONTEXT.md D-14 to D-15 (Context requirements)
  </read_first>
  <action>Create frontend/src/context/SocketContext.tsx:

```typescript
// frontend/src/context/SocketContext.tsx
'use client';

import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { Socket } from 'socket.io-client';
import { createSocket } from '@/lib/socket';
import type { AttackEvent } from '@/types/attack';

type ConnectionStatus = 'connected' | 'disconnected' | 'reconnecting';

interface SocketState {
  status: ConnectionStatus;
  attacks: AttackEvent[];
}

type SocketAction =
  | { type: 'CONNECTED' }
  | { type: 'DISCONNECTED' }
  | { type: 'RECONNECTING' }
  | { type: 'NEW_ATTACK'; payload: AttackEvent };

const initialState: SocketState = {
  status: 'disconnected',
  attacks: [],
};

function socketReducer(state: SocketState, action: SocketAction): SocketState {
  switch (action.type) {
    case 'CONNECTED':
      return { ...state, status: 'connected' };
    case 'DISCONNECTED':
      return { ...state, status: 'disconnected' };
    case 'RECONNECTING':
      return { ...state, status: 'reconnecting' };
    case 'NEW_ATTACK':
      // Prepend new attacks, cap at 100 for memory
      return {
        ...state,
        attacks: [action.payload, ...state.attacks].slice(0, 100),
      };
    default:
      return state;
  }
}

const SocketContext = createContext<{
  state: SocketState;
} | null>(null);

export function SocketProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(socketReducer, initialState);

  useEffect(() => {
    const socket: Socket = createSocket();

    socket.on('connect', () => {
      console.log('[Socket] Connected to backend');
      dispatch({ type: 'CONNECTED' });
    });

    socket.on('disconnect', () => {
      console.log('[Socket] Disconnected from backend');
      dispatch({ type: 'DISCONNECTED' });
    });

    socket.io.on('reconnect_attempt', () => {
      console.log('[Socket] Reconnecting...');
      dispatch({ type: 'RECONNECTING' });
    });

    socket.on('attack_event', (attack: AttackEvent) => {
      console.log('[Socket] Received attack:', attack.archetype, attack.ip);
      dispatch({ type: 'NEW_ATTACK', payload: attack });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <SocketContext.Provider value={{ state }}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within SocketProvider');
  }
  return context;
}
```

Per D-14: React Context + useReducer for connection state and received attacks.
Per D-15: Context provides connection status and attacks array.</action>
  <verify>
    <automated>grep -q "useReducer" frontend/src/context/SocketContext.tsx && grep -q "attack_event" frontend/src/context/SocketContext.tsx && grep -q "useSocket" frontend/src/context/SocketContext.tsx && grep -q "SocketProvider" frontend/src/context/SocketContext.tsx</automated>
  </verify>
  <done>frontend/src/context/SocketContext.tsx exists with SocketProvider, useSocket hook, and useReducer for state management.</done>
</task>

<task type="auto">
  <name>Task 3: Create ConnectionStatus component</name>
  <files>frontend/src/components/ConnectionStatus.tsx</files>
  <read_first>
    - frontend/src/context/SocketContext.tsx (for useSocket import)
    - DESIGN.md (for phosphor green color, LIVE badge styling)
  </read_first>
  <action>Create frontend/src/components/ConnectionStatus.tsx:

```typescript
// frontend/src/components/ConnectionStatus.tsx
'use client';

import { useSocket } from '@/context/SocketContext';

/**
 * Displays connection status to backend:
 * - Connected: "LIVE" badge with phosphor green glow pulse
 * - Reconnecting: "Reconnecting..." amber warning
 * - Disconnected: "SIGNAL LOST" red banner
 */
export function ConnectionStatus() {
  const { state } = useSocket();

  if (state.status === 'connected') {
    return (
      <div className="flex items-center gap-2">
        {/* Animated glow pulse */}
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-phosphor opacity-75" />
          <span className="relative inline-flex rounded-full h-3 w-3 bg-phosphor" />
        </span>
        <span className="font-mono text-sm text-phosphor font-semibold tracking-wide">
          LIVE
        </span>
      </div>
    );
  }

  if (state.status === 'reconnecting') {
    return (
      <div className="bg-amber/20 text-amber px-4 py-2 rounded-md font-mono text-sm">
        Reconnecting...
      </div>
    );
  }

  // Disconnected
  return (
    <div className="bg-alert/20 text-alert px-4 py-2 rounded-md font-mono text-sm font-semibold tracking-wide">
      SIGNAL LOST
    </div>
  );
}
```

Per RTCL-03: "SIGNAL LOST" banner displayed on dashboard during disconnect.
Per RTCL-04: Connection state displayed via "LIVE" badge with phosphor green glow pulse.

Styling uses DESIGN.md tokens:
- Phosphor green (#00FF88) for LIVE badge
- Amber (#FFB800) for reconnecting
- Alert red (#FF3B5C) for SIGNAL LOST
- Font: IBM Plex Mono (font-mono)
- Glow pulse: 1.5s ease-in-out infinite (animate-ping)</action>
  <verify>
    <automated>grep -q "SIGNAL LOST" frontend/src/components/ConnectionStatus.tsx && grep -q "LIVE" frontend/src/components/ConnectionStatus.tsx && grep -q "bg-phosphor" frontend/src/components/ConnectionStatus.tsx && grep -q "animate-ping" frontend/src/components/ConnectionStatus.tsx</automated>
  </verify>
  <done>frontend/src/components/ConnectionStatus.tsx exists showing LIVE badge (connected), Reconnecting (amber), or SIGNAL LOST (disconnected).</done>
</task>

<task type="auto">
  <name>Task 4: Update layout with SocketProvider</name>
  <files>frontend/src/app/layout.tsx</files>
  <read_first>
    - frontend/src/app/layout.tsx (current content from Plan 02)
    - frontend/src/context/SocketContext.tsx (for SocketProvider import)
  </read_first>
  <action>Update frontend/src/app/layout.tsx to wrap children with SocketProvider:

1. Import SocketProvider:
   ```typescript
   import { SocketProvider } from '@/context/SocketContext';
   ```

2. Wrap children in the return:
   ```typescript
   <body className={`${dmSans.variable} ${ibmPlexMono.variable} font-body bg-background text-text-primary`}>
     <SocketProvider>
       {children}
     </SocketProvider>
   </body>
   ```

3. Ensure 'use client' is NOT on layout.tsx (it's a Server Component).
   - SocketProvider has 'use client' directive
   - layout.tsx remains a Server Component

Per RTCL-01: Socket.io client connects on page load (via SocketProvider useEffect).</action>
  <verify>
    <automated>grep -q "SocketProvider" frontend/src/app/layout.tsx && ! grep -q "'use client'" frontend/src/app/layout.tsx</automated>
  </verify>
  <done>frontend/src/app/layout.tsx wraps children with SocketProvider, enabling socket connection on page load.</done>
</task>

<task type="auto">
  <name>Task 5: Create dashboard page with connection status</name>
  <files>frontend/src/app/page.tsx</files>
  <read_first>
    - frontend/src/components/ConnectionStatus.tsx (for import)
    - frontend/src/context/SocketContext.tsx (for useSocket if displaying attack count)
    - DESIGN.md (for layout and styling)
  </read_first>
  <action>Create frontend/src/app/page.tsx as the dashboard:

```typescript
// frontend/src/app/page.tsx
'use client';

import { ConnectionStatus } from '@/components/ConnectionStatus';
import { useSocket } from '@/context/SocketContext';

export default function Dashboard() {
  const { state } = useSocket();

  return (
    <main className="min-h-screen bg-background text-text-primary">
      {/* Header */}
      <header className="flex items-center justify-between px-lg py-md border-b border-border">
        <h1 className="font-display text-h1 text-text-primary">
          Holding Cell
        </h1>
        <ConnectionStatus />
      </header>

      {/* Main content area */}
      <div className="p-lg">
        {/* Connection status info */}
        <div className="mb-lg">
          <p className="text-text-muted font-mono text-sm">
            {state.status === 'connected' && `Connected — ${state.attacks.length} attacks received`}
            {state.status === 'reconnecting' && 'Attempting to reconnect...'}
            {state.status === 'disconnected' && 'Waiting for connection...'}
          </p>
        </div>

        {/* Placeholder for Phase 2: JailCellGrid */}
        <div className="bg-surface rounded-lg p-xl border border-border">
          <p className="text-text-muted font-body">
            [Jail Cell Grid will be implemented in Phase 2]
          </p>
          {state.attacks.length > 0 && (
            <div className="mt-md">
              <p className="text-text-muted font-mono text-sm mb-sm">
                Recent attacks (last {Math.min(5, state.attacks.length)}):
              </p>
              <ul className="font-mono text-sm space-y-xs">
                {state.attacks.slice(0, 5).map((attack) => (
                  <li key={attack.id} className="text-phosphor">
                    [{attack.archetype}] {attack.ip} — {attack.country}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Placeholder for Phase 2: StatsPanel */}
        <div className="mt-lg bg-surface rounded-lg p-md border border-border">
          <p className="text-text-muted font-body text-sm">
            [Stats Panel will be implemented in Phase 2]
          </p>
        </div>
      </div>
    </main>
  );
}
```

This dashboard:
- Shows connection status in header (LIVE/SIGNAL LOST/Reconnecting)
- Displays attack count when connected
- Shows last 5 attacks for debugging (Phase 1 only)
- Includes placeholders for Phase 2 components (JailCellGrid, StatsPanel)

Uses DESIGN.md styling:
- bg-background (#0D0D0D)
- text-text-primary (#F0F0F0)
- font-display (Satoshi) for H1
- font-mono (IBM Plex Mono) for attack logs
- bg-surface (#1A1A1A) for cards</action>
  <verify>
    <automated>grep -q "ConnectionStatus" frontend/src/app/page.tsx && grep -q "useSocket" frontend/src/app/page.tsx && grep -q "Holding Cell" frontend/src/app/page.tsx && grep -q "'use client'" frontend/src/app/page.tsx</automated>
  </verify>
  <done>frontend/src/app/page.tsx exists as dashboard showing connection status and recent attacks for Phase 1 debugging.</done>
</task>

</tasks>

<verification>
## Frontend Socket.io Verification Commands

1. **Start backend server:**
   ```bash
   cd backend && python main.py
   ```

2. **Start frontend dev server:**
   ```bash
   cd frontend && npm run dev
   ```

3. **Verify connection:**
   - Open http://localhost:3000
   - Should see "LIVE" badge with green glow when connected
   - Backend console shows: "Client connected: <sid>"
   - Frontend console shows: "[Socket] Connected to backend"

4. **Verify disconnect handling:**
   - Stop backend server (Ctrl+C)
   - Frontend should show "SIGNAL LOST" banner
   - Frontend console shows: "[Socket] Disconnected from backend"
   - Restart backend
   - Frontend should reconnect and show "LIVE" again

5. **Verify attack events:**
   - When connected, frontend should receive attack events every 3-8 seconds
   - Frontend console shows: "[Socket] Received attack: <archetype> <ip>"
   - Dashboard shows attack count incrementing

6. **Verify reconnection:**
   - Stop and restart backend multiple times
   - Frontend should auto-reconnect with exponential backoff
</verification>

<success_criteria>
- [ ] Socket.io client connects to ws://localhost:8000 on page load
- [ ] "LIVE" badge displays with phosphor green glow when connected
- [ ] "SIGNAL LOST" banner displays when disconnected
- [ ] "Reconnecting..." displays during reconnection attempts
- [ ] Client auto-reconnects with exponential backoff (1s, 2s, 4s, max 30s)
- [ ] Attack events received from socket stored in context state
- [ ] Dashboard shows connection status and attack count
- [ ] No React hydration errors in console
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/03-SUMMARY.md`
</output>