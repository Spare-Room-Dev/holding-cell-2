"""
FastAPI + python-socketio ASGI server for The Holding Cell.

Per BACK-01: FastAPI server runs on port 8000 with async support
Per BACK-02: python-socketio AsyncServer handles WebSocket connections
Per D-07: CowrieReader processes real attacks from Cowrie honeypot
Per D-09: Socket emit failures logged with try/catch, no crash
Per SEC-02: WebSocket authentication token validation
"""

import asyncio
import os
import socketio
from fastapi import FastAPI
import uvicorn

from cowrie_reader import CowrieReader
from geoip_service import GeoIPService
from persistence import PersistenceManager


# Per SEC-02: WebSocket authentication token from environment
WEBSOCKET_AUTH_TOKEN = os.environ.get('WEBSOCKET_AUTH_TOKEN', '')

# Per BACK-01: FastAPI app initialization
app = FastAPI(
    title="The Holding Cell - Backend",
    description="Honeypot attack visualization backend server",
    version="1.0.0",
)

# Per BACK-02: python-socketio AsyncServer with CORS
# Per D-04: CORS allows configured origins from environment
# Note: cors_credentials=True required for WebSocket-only transport
# Note: Using callable for cors_allowed_origins because list-based validation
# doesn't work correctly with WebSocket-only transport in python-engineio.
# See: https://github.com/miguelgrinberg/python-socketio/discussions/1247
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')

# Per D-20/D-21: GeoIP service for country lookups
# Per D-07: CowrieReader replaces attack_generator
# Per STORE-01/STAT-01: Persistence manager for attack history
geoip_service = None
cowrie_reader = None
persistence_manager = None


def validate_origin(origin, environ=None):
    """Validate origin for CORS. Returns True if origin is allowed."""
    if origin is None:
        return False
    # Support both with and without environ argument for compatibility
    return origin in ALLOWED_ORIGINS


sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=validate_origin,
    cors_credentials=True,
)

# Per Pattern 1: ASGIApp wrapper to combine FastAPI and Socket.io
combined_app = socketio.ASGIApp(sio, app)


# Socket.IO event handlers
@sio.event
async def connect(sid: str, environ: dict, auth: dict) -> bool:
    """
    Handle client connection.

    Per D-05: Send history on connect.
    Per STORE-03: New clients immediately see existing attacks on connect.
    Per SEC-02: Validate authentication token before allowing connection.

    Args:
        sid: Socket.io session ID
        environ: WSGI environment dict
        auth: Authentication data from client

    Returns:
        bool: True to accept connection, False to reject
    """
    # Per SEC-02: Validate auth token if configured
    if WEBSOCKET_AUTH_TOKEN:
        if not auth:
            print(f"[Socket.IO] Rejected connection from {sid}: no auth provided")
            return False
        token = auth.get('token', '')
        if token != WEBSOCKET_AUTH_TOKEN:
            print(f"[Socket.IO] Rejected connection from {sid}: invalid token")
            return False

    print(f"[Socket.IO] Client connected: {sid}")

    # Per D-05/D-06/D-07: Send history on connect
    # Per STORE-02: All clients receive same history from in-memory cache
    if persistence_manager:
        await sio.emit('attack_history', {
            'attacks': persistence_manager.get_history(),
            'lifetime_count': persistence_manager.get_lifetime_count(),
            'analytics': persistence_manager.get_analytics()
        }, to=sid)

    return True  # Explicitly return True to accept connection


@sio.event
async def disconnect(sid: str) -> None:
    """
    Handle client disconnection.

    Args:
        sid: Socket.io session ID
    """
    print(f"[Socket.IO] Client disconnected: {sid}")


# Per D-07: CowrieReader replaces attack_generator for real attack data
# Per D-08: Fake attack generator disabled entirely
# Per D-12: Throttled emission (1.5s buffer) handled in CowrieReader
# Per D-13: Socket.io still uses same attack_event channel
async def cowrie_emitter() -> None:
    """
    Background task that watches Cowrie logs and emits real attacks.

    Replaces the fake attack_emitter with real honeypot data.
    """
    print("[CowrieEmitter] Starting Cowrie log watcher...")

    # Initialize GeoIP service
    global geoip_service
    geoip_service = GeoIPService()

    # Initialize Cowrie reader
    global cowrie_reader
    cowrie_reader = CowrieReader(geoip_service=geoip_service)

    # Process existing log entries first
    await cowrie_reader.process_existing_log()

    # Define emit callback for Socket.io
    async def emit_attack(attack_dict: dict) -> None:
        try:
            await sio.emit('attack_event', attack_dict)
            # Per D-03/D-08: Persist immediately after emission
            # Per STORE-01: Persist every attack for crash recovery
            if persistence_manager:
                await persistence_manager.add_attack(attack_dict)
        except Exception as e:
            print(f"[CowrieEmitter] Failed to emit/persist attack: {e}")

    # Start watching for new entries
    await cowrie_reader.watch_log(emit_callback=emit_attack)


# Per BACK-01: Health check endpoint
@app.get('/health')
async def health_check() -> dict:
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Status indicator
    """
    return {"status": "ok"}


# Per Pattern 1: Startup event to create background task
@app.on_event('startup')
async def startup() -> None:
    """Start server with persistence and Cowrie log watcher."""
    global persistence_manager

    # Per D-07: Load history from JSON file into memory on startup
    persistence_manager = PersistenceManager()
    await persistence_manager.load()

    # Start Cowrie watcher
    asyncio.create_task(cowrie_emitter())
    print("[FastAPI] Server started, persistence loaded, Cowrie watcher running")


# Per BACK-01: Main block - uvicorn runs combined app on port 8000
if __name__ == '__main__':
    print("=" * 60)
    print("The Holding Cell - Backend Server")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:8000")
    print("WebSocket endpoint: ws://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("=" * 60)

    uvicorn.run(
        combined_app,
        host='0.0.0.0',
        port=8000,
    )