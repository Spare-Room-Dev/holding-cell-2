// frontend/src/context/SocketContext.tsx
'use client';

import { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { Socket } from 'socket.io-client';
import { createSocket } from '@/lib/socket';
import type { AttackEvent, Analytics, AttackHistoryPayload } from '@/types/attack';

type ConnectionStatus = 'connected' | 'disconnected' | 'reconnecting';

interface SocketState {
  status: ConnectionStatus;
  attacks: AttackEvent[];
  lifetimeCount: number;      // cumulative attack count
  analytics: Analytics;        // aggregations
}

type SocketAction =
  | { type: 'CONNECTED' }
  | { type: 'DISCONNECTED' }
  | { type: 'RECONNECTING' }
  | { type: 'NEW_ATTACK'; payload: AttackEvent }
  | { type: 'ATTACK_HISTORY'; payload: AttackHistoryPayload };

const initialState: SocketState = {
  status: 'disconnected',
  attacks: [],
  lifetimeCount: 0,
  analytics: {
    countries: {},
    protocols: {},
    ports: {},
  },
};

function socketReducer(state: SocketState, action: SocketAction): SocketState {
  switch (action.type) {
    case 'CONNECTED':
      return { ...state, status: 'connected' };
    case 'DISCONNECTED':
      return { ...state, status: 'disconnected' };
    case 'RECONNECTING':
      return { ...state, status: 'reconnecting' };
    case 'ATTACK_HISTORY':
      return {
        ...state,
        status: 'connected',
        attacks: action.payload.attacks,
        lifetimeCount: action.payload.lifetime_count,
        analytics: action.payload.analytics,
      };
    case 'NEW_ATTACK': {
      const attack = action.payload;
      const newAnalytics = { ...state.analytics };

      // Update country count
      newAnalytics.countries[attack.countryCode] =
        (newAnalytics.countries[attack.countryCode] || 0) + 1;

      // Update protocol count
      newAnalytics.protocols[attack.protocol] =
        (newAnalytics.protocols[attack.protocol] || 0) + 1;

      // Update port count (convert to string for object key)
      const portStr = String(attack.port);
      newAnalytics.ports[portStr] =
        (newAnalytics.ports[portStr] || 0) + 1;

      return {
        ...state,
        attacks: [attack, ...state.attacks].slice(0, 100),
        lifetimeCount: state.lifetimeCount + 1,
        analytics: newAnalytics,
      };
    }
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

    socket.on('attack_history', (data: AttackHistoryPayload) => {
      console.log('[Socket] Received attack history:', data.attacks.length, 'attacks');
      dispatch({ type: 'ATTACK_HISTORY', payload: data });
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