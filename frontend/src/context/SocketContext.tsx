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