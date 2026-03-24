// frontend/src/app/page.tsx
'use client';

import { ConnectionStatus } from '@/components/ConnectionStatus';
import { useSocket } from '@/context/SocketContext';
import { Archetype } from '@/types/attack';

// Per D-09: Archetype colors matching backend
const ARCHETYPE_COLORS: Record<Archetype, string> = {
  script_kiddie: 'text-amber',      // Yellow/Amber
  botnet_drone: 'text-phosphor',   // Green
  apt_operative: 'text-alert',     // Red
  iot_worm: 'text-purple-400',     // Magenta
  hacktivist: 'text-blue-400',     // Blue
};

function getArchetypeColor(archetype: Archetype): string {
  return ARCHETYPE_COLORS[archetype] || 'text-phosphor';
}

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
                  <li key={attack.id} className={getArchetypeColor(attack.archetype)}>
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