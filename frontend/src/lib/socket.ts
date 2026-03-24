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