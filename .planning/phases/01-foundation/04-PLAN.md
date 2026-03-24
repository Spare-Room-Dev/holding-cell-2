---
phase: 01-foundation
plan: 04
type: execute
wave: 3
depends_on: ["01", "02", "03"]
files_modified:
  - package.json
autonomous: true
requirements:
  - DEV-01
  - DEV-02
  - DEV-03
must_haves:
  truths:
    - "npm run dev:backend starts FastAPI on port 8000"
    - "npm run dev:frontend starts Next.js on port 3000"
    - "npm run dev:all runs both backend and frontend concurrently"
    - "Both servers start and connect successfully"
    - "Backend emits attack events to connected frontend"
    - "Frontend displays LIVE badge when connected"
  artifacts:
    - path: "package.json"
      provides: "Root dev scripts for unified development"
      contains: "dev:backend"
      contains: "dev:frontend"
      contains: "dev:all"
      contains: "concurrently"
  key_links:
    - from: "package.json dev:backend"
      to: "backend/main.py"
      via: "uvicorn main:app --reload --port 8000"
    - from: "package.json dev:frontend"
      to: "frontend/package.json"
      via: "npm run dev"
    - from: "package.json dev:all"
      to: "dev:backend + dev:frontend"
      via: "concurrently"
---

<objective>
Create root package.json with npm workspaces and concurrently-based dev scripts for unified development experience.

Purpose: Enable single-command development workflow (`npm run dev:all`) that starts both backend and frontend.
Output: Working dev commands that start backend on port 8000 and frontend on port 3000 simultaneously.
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
<!-- Key contracts from previous plans and RESEARCH.md. -->

From RESEARCH.md Dev Scripts Pattern:
```json
// Root package.json
{
  "name": "holding-cell",
  "workspaces": ["backend", "frontend"],
  "scripts": {
    "dev:backend": "cd backend && uvicorn main:combined_app --reload --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:all": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\""
  },
  "devDependencies": {
    "concurrently": "^9.0.0"
  }
}
```

From CONTEXT.md D-17 to D-20:
- D-17: Root package.json with concurrently for dev:all
- D-18: Scripts: dev:backend (uvicorn), dev:frontend (next dev), dev:all (both)
- D-19: Python dependencies in backend/requirements.txt
- D-20: Node dependencies in frontend/package.json + root package.json (workspace root)

From PLAN.md Root Dev Scripts:
```
# In root:
dev:backend:
  cd backend && uvicorn main:combined_app --reload --port 8000

dev:frontend:
  cd frontend && npm run dev

dev:all:
  concurrently "npm run dev:backend" "npm run dev:frontend"
```

Note: uvicorn needs to import from main.py. The ASGIApp is stored in `combined_app` variable in main.py (per backend/main.py from Plan 01).
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create root package.json with workspaces and dev scripts</name>
  <files>package.json</files>
  <read_first>
    - backend/main.py (to verify combined_app export name)
    - frontend/package.json (to verify dev script exists)
    - RESEARCH.md Dev Scripts section
    - CONTEXT.md D-17 to D-20
  </read_first>
  <action>Create package.json at project root with:

```json
{
  "name": "holding-cell",
  "version": "0.1.0",
  "private": true,
  "workspaces": ["frontend"],
  "scripts": {
    "dev:backend": "cd backend && uvicorn main:combined_app --reload --port 8000",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:all": "concurrently -n \"backend,frontend\" -c \"bgBlue.bold,green.bold\" \"npm run dev:backend\" \"npm run dev:frontend\""
  },
  "devDependencies": {
    "concurrently": "^9.0.0"
  }
}
```

Key details:
- Workspaces: ["frontend"] (backend is Python, not a workspace)
- dev:backend: Uses uvicorn to run combined_app from main.py
- dev:frontend: Runs Next.js dev server
- dev:all: Uses concurrently with named output (backend/frontend) and colors
- concurrently version: ^9.0.0 (latest stable)

Per DEV-01: npm run dev:backend starts FastAPI on port 8000.
Per DEV-02: npm run dev:frontend starts Next.js on port 3000.
Per DEV-03: npm run dev:all runs both concurrently.

Note: The combined_app variable name comes from backend/main.py (Plan 01 Task 5), which uses `combined_app = socketio.ASGIApp(sio, app)`.</action>
  <verify>
    <automated>grep -q '"dev:backend"' package.json && grep -q '"dev:frontend"' package.json && grep -q '"dev:all"' package.json && grep -q '"concurrently"' package.json && grep -q 'uvicorn main:combined_app' package.json</automated>
  </verify>
  <done>package.json exists at project root with dev:backend, dev:frontend, and dev:all scripts using concurrently.</done>
</task>

</tasks>

<verification>
## Dev Scripts Verification Commands

1. **Install root dependencies:**
   ```bash
   npm install
   ```

2. **Verify concurrently installed:**
   ```bash
   npm list concurrently
   ```

3. **Test dev:backend script:**
   ```bash
   npm run dev:backend
   ```
   - Should start uvicorn on port 8000
   - Should see: "INFO: Uvicorn running on http://0.0.0.0:8000"
   - Should see colored attack logs every 3-8 seconds
   - Ctrl+C to stop

4. **Test dev:frontend script:**
   ```bash
   npm run dev:frontend
   ```
   - Should start Next.js on port 3000
   - Should see: "ready started server on 0.0.0.0:3000"
   - Ctrl+C to stop

5. **Test dev:all script:**
   ```bash
   npm run dev:all
   ```
   - Should start both backend and frontend
   - Backend on port 8000, Frontend on port 3000
   - Output should show both "backend" and "frontend" in different colors
   - Frontend should connect to backend (LIVE badge)
   - Ctrl+C to stop both

6. **End-to-end verification:**
   - Run `npm run dev:all`
   - Open http://localhost:3000
   - Should see "LIVE" badge with green glow
   - Backend console shows colored attack logs
   - Frontend console shows "[Socket] Connected to backend"
   - Dashboard shows "Connected — X attacks received"
</verification>

<success_criteria>
- [ ] `npm run dev:backend` starts FastAPI on port 8000
- [ ] `npm run dev:frontend` starts Next.js on port 3000
- [ ] `npm run dev:all` runs both concurrently with colored output
- [ ] Both servers start successfully and connect
- [ ] Frontend displays "LIVE" badge when connected
- [ ] Backend emits attack events every 3-8 seconds
- [ ] Frontend receives and displays attack events
- [ ] concurrently is installed as dev dependency
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/04-SUMMARY.md`
</output>