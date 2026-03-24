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