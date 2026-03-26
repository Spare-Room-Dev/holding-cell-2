'use client';

interface MethodsPanelProps {
  protocols: Record<string, number>;  // SSH/TELNET -> count
  ports: [string, number][];          // [port, count] pairs, already sorted top 5
}

export function MethodsPanel({ protocols, ports }: MethodsPanelProps) {
  const hasData = Object.keys(protocols).length > 0 || ports.length > 0;

  if (!hasData) {
    return (
      <div className="flex flex-col items-center gap-xs">
        <span className="counter-label">Attack Methods</span>
        <span className="text-text-muted text-sm">No attacks yet</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-xs">
      <span className="counter-label">Attack Methods</span>

      {/* Protocol breakdown */}
      <div className="flex flex-row gap-md text-sm font-mono">
        <div className="flex items-center gap-xs">
          <span className="text-text-muted">SSH:</span>
          <span className="text-primary">
            {(protocols.SSH || 0).toLocaleString()}
          </span>
        </div>
        <div className="flex items-center gap-xs">
          <span className="text-text-muted">Telnet:</span>
          <span className="text-primary">
            {(protocols.TELNET || 0).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Top ports */}
      {ports.length > 0 && (
        <div className="flex flex-col gap-2xs">
          <span className="counter-label text-xs">Top Ports</span>
          {ports.map(([port, count]) => (
            <div
              key={port}
              className="flex items-center gap-xs text-sm font-mono"
            >
              <span className="text-text-muted">{port}:</span>
              <span className="text-primary">
                {count.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}