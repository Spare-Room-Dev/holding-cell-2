---
phase: 01-foundation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - backend/requirements.txt
  - backend/models.py
  - backend/archetypes.py
  - backend/attack_generator.py
  - backend/main.py
autonomous: true
requirements:
  - BACK-01
  - BACK-02
  - BACK-03
  - BACK-04
  - BACK-05
  - BACK-06
  - BACK-07
  - BACK-08
  - BACK-09
  - DEV-04
must_haves:
  truths:
    - "Backend server starts on port 8000"
    - "Fake attack events emit every 3-8 seconds"
    - "AttackEvent contains all required fields (id, timestamp, ip, country, countryCode, port, protocol, archetype, commands, duration, rawLog)"
    - "Archetypes follow weighted distribution (botnet_drone: 50%, script_kiddie: 30%, apt_operative: 10%, iot_worm: 7%, hacktivist: 3%)"
    - "Console logs show colored archetype tags"
    - "Socket emit failures are caught and logged (no crash)"
  artifacts:
    - path: "backend/requirements.txt"
      provides: "Python dependencies"
      contains: "fastapi"
      contains: "python-socketio"
      contains: "uvicorn"
    - path: "backend/models.py"
      provides: "AttackEvent Pydantic model"
      exports: ["AttackEvent", "Archetype", "create_attack_event"]
    - path: "backend/archetypes.py"
      provides: "Archetype classification rules"
      exports: ["ARCHETYPE_WEIGHTS", "choose_archetype", "generate_attack_profile"]
    - path: "backend/attack_generator.py"
      provides: "Fake attack data generation"
      exports: ["AttackGenerator", "generate_fake_attack"]
    - path: "backend/main.py"
      provides: "FastAPI + Socket.io server"
      contains: "ASGIApp"
      contains: "await sio.emit"
  key_links:
    - from: "backend/main.py"
      to: "backend/attack_generator.py"
      via: "import AttackGenerator, create background task"
    - from: "backend/main.py"
      to: "backend/models.py"
      via: "import AttackEvent"
    - from: "backend/attack_generator.py"
      to: "backend/archetypes.py"
      via: "import choose_archetype, generate_attack_profile"
    - from: "backend/attack_generator.py"
      to: "backend/models.py"
      via: "import create_attack_event"
---

<objective>
Create complete Python backend with FastAPI + python-socketio server that generates fake attack events and broadcasts them via WebSocket.

Purpose: Establish real-time data pipeline for dashboard visualization.
Output: Running backend server on port 8000 emitting attack events every 3-8 seconds.
</objective>

<execution_context>
@/Users/rob/Documents/OT Apps/Holding Cell 2/.claude/get-shit-done/workflows/execute-plan.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/PROJECT.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/ROADMAP.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/STATE.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/phases/01-foundation/01-CONTEXT.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/.planning/phases/01-foundation/01-RESEARCH.md
@/Users/rob/Documents/OT Apps/Holding Cell 2/PLAN.md

<interfaces>
<!-- Key contracts executor needs. Extracted from RESEARCH.md patterns. -->

From RESEARCH.md Pattern 1 (FastAPI + python-socketio ASGI Integration):
```python
# Standard pattern for combining FastAPI and Socket.io
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=['http://localhost:3000'])
app = FastAPI()
combined_app = socketio.ASGIApp(sio, app)

# Background task for emitting events
async def attack_emitter():
    while True:
        attack = generate_attack()
        try:
            await sio.emit('attack_event', attack.model_dump())
        except Exception as e:
            print(f'Emit failed: {e}')
        await asyncio.sleep(random.uniform(3, 8))

# Startup event
@app.on_event('startup')
async def startup():
    asyncio.create_task(attack_emitter())
```

From RESEARCH.md Pattern 2 (Socket.io Client):
```typescript
// Exponential backoff configuration per RTCL-02
const SOCKET_URL = 'ws://localhost:8000';
io(SOCKET_URL, {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 30000,
  randomizationFactor: 0.5,
  transports: ['websocket'],
});
```

From CONTEXT.md D-06 (acceptable data loss):
- Events emitted during disconnect are lost — acceptable for Approach A v1
- No retry queue needed

From CONTEXT.md D-08:
- Attack generator emits every 3-8 seconds (randomized interval)

From CONTEXT.md D-09:
- Console logging: colored archetype tag + attack summary (timestamp, archetype, IP)

From REQUIREMENTS.md weighted distribution (BACK-04):
- botnet_drone: 50%
- script_kiddie: 30%
- apt_operative: 10%
- iot_worm: 7%
- hacktivist: 3%

From REQUIREMENTS.md archetype fingerprint rules (BACK-08):
- script_kiddie: <2 min duration, <10 commands, no recon
- botnet_drone: <5 min duration, <20 commands, repeated same passwords
- apt_operative: >10 min duration, >50 commands, has recon (ls, pwd, cat /etc/passwd)
- iot_worm: buildroot/busybox/mips in probe
- hacktivist: username contains anonymous/free/hack

From REQUIREMENTS.md TEST-NET ranges (BACK-06):
- 203.0.113.0/24 (TEST-NET-3)
- 198.51.100.0/24 (TEST-NET-2)
- 192.0.2.0/24 (TEST-NET-1)
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create backend directory and requirements.txt</name>
  <files>backend/requirements.txt</files>
  <read_first>
    - This file does not exist yet (greenfield project)
  </read_first>
  <action>Create backend/ directory and requirements.txt with all Python dependencies:
- fastapi>=0.135.0
- python-socketio[asyncio]>=5.9.0
- uvicorn[standard]>=0.34.0
- pydantic>=2.0.0
- httpx>=0.28.0 (for future Shodan integration)

File content:
```
fastapi>=0.135.0
python-socketio[asyncio]>=5.9.0
uvicorn[standard]>=0.34.0
pydantic>=2.0.0
httpx>=0.28.0
```

Per DEV-04: backend/requirements.txt lists all Python dependencies.</action>
  <verify>
    <automated>test -f backend/requirements.txt && grep -q "fastapi" backend/requirements.txt && grep -q "python-socketio" backend/requirements.txt && grep -q "uvicorn" backend/requirements.txt</automated>
  </verify>
  <done>backend/requirements.txt exists with all required dependencies (fastapi, python-socketio, uvicorn, pydantic, httpx).</done>
</task>

<task type="auto">
  <name>Task 2: Create Pydantic models for AttackEvent</name>
  <files>backend/models.py</files>
  <read_first>
    - PLAN.md Data Model section for AttackEvent structure
  </read_first>
  <action>Create backend/models.py with:

1. Archetype type alias (Literal union of all 5 archetypes)
2. AttackEvent Pydantic model with all fields per BACK-05:
   - id: str (UUID)
   - timestamp: str (ISO 8601)
   - ip: str
   - country: str
   - countryCode: str
   - port: int
   - protocol: str
   - archetype: Archetype
   - commands: list[str]
   - duration: int (seconds)
   - rawLog: str

3. create_attack_event() factory function that generates UUID and timestamp

All fields must match the TypeScript interface that will be created in frontend/src/types/attack.ts (keep in sync manually per D-10 to D-13).</action>
  <verify>
    <automated>grep -q "class AttackEvent" backend/models.py && grep -q "archetype: Archetype" backend/models.py && grep -q "def create_attack_event" backend/models.py</automated>
  </verify>
  <done>backend/models.py exists with AttackEvent Pydantic model, Archetype type, and create_attack_event factory function.</done>
</task>

<task type="auto">
  <name>Task 3: Create archetype classification module</name>
  <files>backend/archetypes.py</files>
  <read_first>
    - backend/models.py (for Archetype type import)
  </read_first>
  <action>Create backend/archetypes.py with:

1. ARCHETYPE_WEIGHTS dictionary per BACK-04:
   - botnet_drone: 50
   - script_kiddie: 30
   - apt_operative: 10
   - iot_worm: 7
   - hacktivist: 3

2. COUNTRY_WEIGHTS dictionary per BACK-07:
   - Weighted toward realistic attacker origins (Russia, China, Brazil, Iran, North Korea, Indonesia)
   - Include countryCode for each

3. TEST_NET_RANGES per BACK-06:
   - 203.0.113.0/24 (TEST-NET-3)
   - 198.51.100.0/24 (TEST-NET-2)
   - 192.0.2.0/24 (TEST-NET-1)

4. ARCHETYPE_PROFILES dictionary per BACK-08:
   - Each archetype has duration range, command count range, command templates, and detection rules
   - script_kiddie: <2min, <10cmds, no recon
   - botnet_drone: <5min, <20cmds, repeated passwords
   - apt_operative: >10min, >50cmds, recon commands
   - iot_worm: buildroot/busybox/mips patterns
   - hacktivist: anonymous/free/hack in username

5. choose_archetype() - weighted random selection
6. choose_country() - weighted random selection
7. generate_ip() - random IP from TEST-NET ranges
8. generate_attack_profile(archetype) - returns duration, commands, rawLog based on archetype fingerprint

All functions should be pure (no side effects) for easy testing.</action>
  <verify>
    <automated>grep -q "ARCHETYPE_WEIGHTS" backend/archetypes.py && grep -q "choose_archetype" backend/archetypes.py && grep -q "TEST_NET_RANGES" backend/archetypes.py && grep -q "generate_attack_profile" backend/archetypes.py</automated>
  </verify>
  <done>backend/archetypes.py exists with weighted archetype selection, country selection, TEST-NET IP generation, and attack profile generation.</done>
</task>

<task type="auto">
  <name>Task 4: Create fake attack generator</name>
  <files>backend/attack_generator.py</files>
  <read_first>
    - backend/models.py (for create_attack_event)
    - backend/archetypes.py (for choose_archetype, generate_attack_profile, choose_country, generate_ip)
  </read_first>
  <action>Create backend/attack_generator.py with:

1. generate_fake_attack() function that:
   - Calls choose_archetype() to get archetype
   - Calls generate_attack_profile(archetype) to get duration, commands, rawLog
   - Calls choose_country() to get country and countryCode
   - Calls generate_ip() to get fake IP
   - Generates random port (common: 22, 80, 443, 8080, etc.)
   - Generates random protocol (SSH, HTTP, HTTPS)
   - Calls create_attack_event() with all data
   - Returns complete AttackEvent

2. Colored console logging per D-09:
   - Format: `[ARCHETYPE_NAME] IP - country (duration, X commands)`
   - Use ANSI color codes for archetype tags
   - Example: `\033[92m[BOTNET_DRONE]\033[0m 203.0.113.42 - China (127s, 15 commands)`

The generator should be a pure function that produces a complete AttackEvent ready for Socket.io emission.</action>
  <verify>
    <automated>grep -q "def generate_fake_attack" backend/attack_generator.py && grep -q "create_attack_event" backend/attack_generator.py</automated>
  </verify>
  <done>backend/attack_generator.py exists with generate_fake_attack() function that produces complete AttackEvent objects with colored console logging.</done>
</task>

<task type="auto">
  <name>Task 5: Create FastAPI + Socket.io server</name>
  <files>backend/main.py</files>
  <read_first>
    - backend/models.py (for AttackEvent)
    - backend/attack_generator.py (for generate_fake_attack)
    - RESEARCH.md Pattern 1 (ASGIApp integration pattern)
  </read_first>
  <action>Create backend/main.py with:

1. FastAPI app initialization (BACK-01)
2. python-socketio AsyncServer with CORS for localhost:3000 (BACK-02, D-04)
3. ASGIApp wrapper to combine FastAPI and Socket.io
4. Socket event handlers:
   - connect(sid, environ, auth) - log connection
   - disconnect(sid) - log disconnection

5. Background attack emitter task (BACK-03):
   - Use asyncio.create_task() on startup
   - Loop forever with random.uniform(3, 8) delay per D-08
   - Call generate_fake_attack() to get event
   - await sio.emit('attack_event', event.model_dump()) with try/except per BACK-09
   - On exception, log error and continue (no crash)

6. Health check endpoint: GET /health returns {"status": "ok"}

7. Main block: uvicorn.run(combined_app, host='0.0.0.0', port=8000)

Per BACK-09: All emit calls wrapped in try/except to prevent crashes on socket disconnect.

Critical: Use `await sio.emit()` (async) not `sio.emit()` (sync) per BACK-02.</action>
  <verify>
    <automated>grep -q "AsyncServer" backend/main.py && grep -q "ASGIApp" backend/main.py && grep -q "await sio.emit" backend/main.py && grep -q "asyncio.create_task" backend/main.py && grep -q "random.uniform(3, 8)" backend/main.py</automated>
  </verify>
  <done>backend/main.py exists with FastAPI + Socket.io ASGIApp integration, background attack emitter running every 3-8 seconds, and proper error handling.</done>
</task>

</tasks>

<verification>
## Backend Verification Commands

1. **Install dependencies:**
   ```bash
   cd backend && pip install -r requirements.txt
   ```

2. **Start backend server:**
   ```bash
   cd backend && python main.py
   ```

3. **Verify server running:**
   - Server starts on port 8000
   - Health check at http://localhost:8000/health returns {"status": "ok"}
   - Console shows colored archetype logs every 3-8 seconds

4. **Verify no crashes on simulated disconnect:**
   - Server should continue running even if no clients connected
   - try/except should catch any emit failures gracefully
</verification>

<success_criteria>
- [ ] Backend server starts successfully on port 8000
- [ ] GET /health returns {"status": "ok"}
- [ ] Console shows colored archetype logs every 3-8 seconds
- [ ] AttackEvent contains all required fields
- [ ] Archetype distribution follows weighted percentages
- [ ] IPs are from TEST-NET ranges only
- [ ] Countries weighted toward realistic attacker origins
- [ ] try/except around all emit calls prevents crashes
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/01-SUMMARY.md`
</output>