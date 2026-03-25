'use client';

import { useMemo } from 'react';
import { useSocket } from '@/context/SocketContext';
import { CounterBox } from './CounterBox';
import type { Archetype } from '@/types/attack';

const ARCHETYPE_LABELS: Record<Archetype, string> = {
  script_kiddie: 'Script Kiddies',
  apt_operative: 'APT Operatives',
  botnet_drone: 'Botnet Drones',
  iot_worm: 'IoT Worms',
  hacktivist: 'Hacktivists',
};

export function StatsPanel() {
  const { state } = useSocket();

  const counts = useMemo(() => {
    const total = state.attacks.length;
    const byArchetype = state.attacks.reduce((acc, attack) => {
      acc[attack.archetype] = (acc[attack.archetype] || 0) + 1;
      return acc;
    }, {} as Record<Archetype, number>);

    return { total, byArchetype };
  }, [state.attacks]);

  return (
    <div className="flex flex-row gap-md flex-wrap">
      {/* Total Attacks counter */}
      <CounterBox label="Total" value={counts.total} />

      {/* Archetype counters */}
      {Object.entries(ARCHETYPE_LABELS).map(([archetype, label]) => (
        <CounterBox
          key={archetype}
          label={label}
          value={counts.byArchetype[archetype as Archetype] || 0}
        />
      ))}
    </div>
  );
}