# CLAUDE.md

## gstack

**Web Browsing:** Always use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

### Available Skills

- `/office-hours` — Office hours workflow
- `/plan-ceo-review` — Plan CEO review
- `/plan-eng-review` — Plan engineering review
- `/plan-design-review` — Plan design review
- `/design-consultation` — Design consultation
- `/review` — Code review
- `/ship` — Ship workflow
- `/land-and-deploy` — Land and deploy
- `/canary` — Canary deployment
- `/benchmark` — Benchmarking
- `/browse` — Web browsing (use this instead of mcp__claude-in-chrome__* tools)
- `/qa` — Quality assurance
- `/qa-only` — QA only (no other steps)
- `/design-review` — Design review
- `/setup-browser-cookies` — Set up browser cookies
- `/setup-deploy` — Set up deployment
- `/retro` — Retrospective
- `/investigate` — Investigation
- `/document-release` — Document a release
- `/codex` — Codex
- `/cso` — CSO workflow
- `/autoplan` — Automatic planning
- `/careful` — Careful mode
- `/freeze` — Freeze deployments
- `/guard` — Guard mode
- `/unfreeze` — Unfreeze deployments
- `/gstack-upgrade` — Upgrade gstack

## Design System
Always read DESIGN.md before making any visual or UI decisions.
All font choices, colors, spacing, and aesthetic direction are defined there.
Do not deviate without explicit user approval.
In QA mode, flag any code that doesn't match DESIGN.md.
