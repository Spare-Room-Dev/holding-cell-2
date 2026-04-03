---
status: resolved
trigger: "WebSocket connection to backend returns 403 Forbidden. Started after Phase 4 implementation. Running via npm run dev:all."
created: 2026-03-26T12:00:00.000Z
updated: 2026-03-26T13:00:00.000Z
---

## Current Focus
hypothesis: CONFIRMED - List-based cors_allowed_origins not working for WebSocket-only transport
test: Tested with custom callable validator - WebSocket upgrade succeeds
expecting: Callable-based validator works, list-based does not
next_action: Implement fix by changing cors_allowed_origins from list to callable

## Symptoms
expected: WebSocket connects and attacks appear in real-time dashboard
actual: WebSocket /socket.io/ returns 403 Forbidden, connection rejected and closed
errors: "[backend] INFO: 127.0.0.1:61339 - 'WebSocket /socket.io/?EIO=4&transport=websocket' 403" and "[backend] INFO: connection rejected (403 Forbidden)"
reproduction: npm run dev:all
started: After implementing Phase 4 (polish - responsive layout, theme toggle)

## Eliminated

## Evidence
- timestamp: 2026-03-26T12:00:00.000Z
  checked: Context notes CORS fix was just committed (cors_credentials=True, added 127.0.0.1 origin)
  found: CORS fix exists but error continues - suggests issue is not simple CORS headers
  implication: Need to investigate Socket.IO-specific origin validation

- timestamp: 2026-03-26T12:05:00.000Z
  checked: backend/main.py CORS configuration
  found: cors_allowed_origins=['http://localhost:3000', 'http://127.0.0.1:3000'], cors_credentials=True
  implication: CORS config looks correct for both localhost and 127.0.0.1 origins

- timestamp: 2026-03-26T12:10:00.000Z
  checked: frontend/src/lib/socket.ts client configuration
  found: SOCKET_URL='ws://localhost:8000', transports=['websocket'] (WebSocket-only, no polling)
  implication: WebSocket-only transport skips HTTP polling handshake, which may affect CORS validation

- timestamp: 2026-03-26T12:15:00.000Z
  checked: Research on python-socketio WebSocket CORS issues
  found: Per GitHub discussion #1247, 403 errors often occur when mixing FastAPI/Socket.IO ASGI incorrectly
  implication: Need to verify ASGIApp configuration and check if WebSocket-only transport requires special handling

- timestamp: 2026-03-26T12:30:00.000Z
  checked: python-engineio source code for origin validation logic (base_server.py, async_server.py)
  found: `_cors_allowed_origins` method handles list vs callable differently. List returns list directly; callable returns [origin] if allowed
  implication: The origin validation logic has subtle differences between list and callable modes

- timestamp: 2026-03-26T12:45:00.000Z
  checked: Tested WebSocket upgrade with curl and custom callable validator
  found: Both `http://localhost:3000` and `http://127.0.0.1:3000` origins return 101 Switching Protocols (success)
  implication: Custom callable validator works correctly, confirming the issue is with list-based cors_allowed_origins

- timestamp: 2026-03-26T12:50:00.000Z
  checked: Compared _cors_allowed_origins behavior for list vs callable
  found: When callable returns True, allowed_origins=[origin], so origin in allowed_origins is always True. When list is used, must match exactly.
  implication: ROOT CAUSE: List-based cors_allowed_origins not working correctly for WebSocket-only transport in python-engineio

## Resolution
root_cause: List-based `cors_allowed_origins` parameter not working correctly for WebSocket-only transport in python-engineio. The origin validation logic in `_cors_allowed_origins` handles list and callable modes differently, with the list-based approach failing to properly validate WebSocket origins.
fix: Changed `cors_allowed_origins` from list to a callable function that explicitly validates origins.
verification: |
  - curl test with Origin: http://localhost:3000 -> 101 Switching Protocols (success)
  - curl test with Origin: http://127.0.0.1:3000 -> 101 Switching Protocols (success)
  - curl test with Origin: http://evil.com -> 403 Forbidden (correctly rejected)
files_changed: ["backend/main.py"]