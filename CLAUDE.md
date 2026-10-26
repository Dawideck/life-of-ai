# Instructions for the implementing agent

You are implementing **life-of-ai**. Read this file first, then `docs/PLAN-mvp.md`. Decisions already made are recorded in `docs/decisions/`; do not reopen them without asking.

## The project in one paragraph

A Python engine (`engine/`) runs an LLM agent in a small voxel world **locally** and writes a JSONL log. A static browser app (`web/`) replays that log as an isometric 3D scene. The two sides share only the JSON Schemas in `schema/`. The web app is deployed as static files to `lifeofai.adnered.net`. Nothing AI-related ever runs on the server.

## Working rules

**Git and PRs**
- Never commit directly to `main`. Branch per task: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`, `chore/<short-name>`.
- One milestone (or a clearly separable part of one) per PR. Keep PRs reviewable.
- Conventional commit messages (`feat(engine): ...`, `fix(web): ...`, `test(engine): ...`, `docs: ...`).
- PR description: what changed, how it was tested, which acceptance criteria from `docs/PLAN-mvp.md` it covers, anything left open.
- Run the relevant tests and linters locally before opening a PR. CI must be green.

**Never**
- Commit `.env`, `.envrc`, tokens, keys, `runs/`, model files, or any log that is not a deliberate test fixture.
- Access, SSH into, or modify the VPS. Server steps are done by the human from `docs/runbooks/vps-setup.md`. You may prepare configs and scripts for them.
- Change repository settings, branch rules or secrets.
- Add a dependency without a one-line justification in the PR description.
- Run long or expensive experiment runs without being asked. Short runs (a few steps) to verify that code works are fine.

**Contracts**
- `schema/world.schema.json` and `schema/log.schema.json` are the contract between `engine/` and `web/`.
- A change to a schema must, in the same PR: update both sides, bump `schema_version` if the change is breaking, and update fixtures and tests.
- The engine validates everything it writes against the schema in tests. The web app validates what it reads and reports problems instead of crashing.

**Coordinates**
- The engine is **z-up**: positions are `[x, y, z]`, z = height of the bottom of the thing.
- Grids (`heights`, `ocean`) are indexed `[y][x]` (row-major, row 0 is the north edge).
- Three.js is **y-up**. Convert in exactly one helper in `web/` and test it.

## Stack and commands

**engine/** — Python 3.12, `uv`, `pytest`, `ruff`.
```
cd engine
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run lifeofai --help
```

**web/** — Node LTS, Vite, TypeScript (strict), Three.js, Vitest, Playwright.
```
cd web
npm ci
npm run typecheck && npm run lint
npm test            # vitest
npm run test:e2e    # playwright
npm run build       # -> web/dist
```

Keep `web/` free of a UI framework for the MVP (plain TS + DOM). Bundle everything; no runtime CDN requests (the site ships a strict Content-Security-Policy).

## Style

- Code, comments, docs and commit messages in English.
- Small, pure functions where possible (especially physics and `observe()`), so they are easy to test.
- Invalid agent actions never raise; they return `ok: false` with a helpful message.
- Prefer clear names over comments. Comment the *why*, not the *what*.

## When unsure

If the plan is ambiguous or contradicts itself, stop and ask in the PR or in the session rather than guessing on anything that is hard to undo (schema shape, world rules, public URLs). For small, easily reversible choices, decide, and note the decision in the PR description.
