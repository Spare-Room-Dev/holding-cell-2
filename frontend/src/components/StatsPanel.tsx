'use client';

import { useMemo } from 'react';
import { useSocket } from '@/context/SocketContext';
import { CounterBox } from './CounterBox';
import { CountryList } from './CountryList';
import { MethodsPanel } from './MethodsPanel';
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

  // Derive top 5 countries from analytics (per D-13)
  const topCountries = useMemo(() => {
    const entries = Object.entries(state.analytics.countries);
    return entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5) as [string, number][];
  }, [state.analytics.countries]);

  // Derive top 5 ports from analytics (per D-15)
  const topPorts = useMemo(() => {
    const entries = Object.entries(state.analytics.ports);
    return entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5) as [string, number][];
  }, [state.analytics.ports]);

  return (
    <div className="flex flex-col gap-md">
      {/* Row 1: Archetype counters (existing) */}
      <div className="flex flex-row gap-md flex-wrap">
        <CounterBox label="Total" value={counts.total} />
        {Object.entries(ARCHETYPE_LABELS).map(([archetype, label]) => (
          <CounterBox
            key={archetype}
            label={label}
            value={counts.byArchetype[archetype as Archetype] || 0}
          />
        ))}
      </div>

      {/* Row 2: Analytics row (new, per D-19, D-20) */}
      <div className="flex flex-row gap-md flex-wrap">
        <CounterBox label="Lifetime" value={state.lifetimeCount} />
        <CountryList countries={topCountries} />
        <MethodsPanel
          protocols={state.analytics.protocols}
          ports={topPorts}
        />
      </div>
    </div>
  );
}