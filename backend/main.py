"""
FastAPI + python-socketio ASGI server for The Holding Cell.

Per BACK-01: FastAPI server runs on port 8000 with async support
Per BACK-02: python-socketio AsyncServer handles WebSocket connections
Per BACK-03: AttackGenerator produces fake attack events every 3-8 seconds
Per BACK-09: Socket emit failures logged with try/catch, no crash
"""

import asyncio
import random
import socketio
from fastapi import FastAPI
import uvicorn

from attack_generator import generate_fake_attack


# Per BACK-01: FastAPI app initialization
app = FastAPI(
    title="The Holding Cell - Backend",
    description="Honeypot attack visualization backend server",
    version="1.0.0",
)

# Per BACK-02: python-socketio AsyncServer with CORS for localhost:3000
# Per D-04: CORS allows localhost:3000 only (development)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:3000'],
)

# Per Pattern 1: ASGIApp wrapper to combine FastAPI and Socket.io
combined_app = socketio.ASGIApp(sio, app)


# Socket.IO event handlers
@sio.event
async def connect(sid: str, environ: dict, auth: dict) -> None:
    """
    Handle client connection.

    Args:
        sid: Socket.io session ID
        environ: WSGI environment dict
        auth: Authentication data from client
    """
    print(f"[Socket.IO] Client connected: {sid}")


@sio.event
async def disconnect(sid: str) -> None:
    """
    Handle client disconnection.

    Args:
        sid: Socket.io session ID
    """
    print(f"[Socket.IO] Client disconnected: {sid}")


# Per BACK-03: Background attack emitter task
async def attack_emitter() -> None:
    """
    Background task that emits fake attack events every 3-8 seconds.

    Per D-08: Attack generator emits every 3-8 seconds (randomized interval)
    Per BACK-09: All emit calls wrapped in try/except to prevent crashes
    """
    print("[AttackEmitter] Starting attack emitter background task...")

    # Wait a moment for server to be ready
    await asyncio.sleep(1)

    while True:
        try:
            # Generate a fake attack event
            attack = generate_fake_attack()

            # Per BACK-02: Use await sio.emit() (async) not sio.emit() (sync)
            # Per BACK-09: Wrap emit in try/except to prevent crashes
            try:
                await sio.emit('attack_event', attack.model_dump())
            except Exception as emit_error:
                # Log error but continue - don't crash the server
                print(f"[AttackEmitter] Failed to emit attack: {emit_error}")

        except Exception as e:
            print(f"[AttackEmitter] Error generating attack: {e}")

        # Per D-08: Randomized interval between 3-8 seconds
        delay = random.uniform(3, 8)
        await asyncio.sleep(delay)


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
    """Create background attack emitter task on server startup."""
    asyncio.create_task(attack_emitter())
    print("[FastAPI] Server started, attack emitter running")


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