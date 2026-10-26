# MVP plan

**Goal of the MVP:** a proof of concept that answers one question: *does an Eko-like setup produce interesting, play-like behaviour on a local model?*

**MVP is done when:** a local run of 2–3 sessions × ~50 steps on an Ollama model produces a `log.jsonl`, and that log, dragged onto `https://lifeofai.adnered.net`, replays as an isometric 3D scene where you can see what the agent did and what it was "thinking".

Out of scope for the MVP (see `ROADMAP-fvp.md`): the world builder, publishing logs to the server, authentication, new world mechanics, live streaming.

---

## Part E — Engine (`engine/`, Python, local only)

### Package layout

```
engine/
  pyproject.toml           # package "lifeofai", console script "lifeofai"
  src/lifeofai/
    __init__.py
    cli.py                 # entry point (argparse or typer)
    world.py               # load world.json, state, physics, reset
    actions.py             # action implementations + validation
    observe.py             # state -> text the agent sees (pure)
    agent.py               # session loop, tools, context window
    providers/
      __init__.py          # Provider protocol + factory
      mock.py              # random-but-legal actions, no network
      ollama.py            # native Ollama /api/chat with tools
      openai_compat.py     # any OpenAI-compatible API (later: other "AIs")
      anthropic.py         # optional, behind an extra dependency
    memory.py              # notes file with size cap
    logger.py              # JSONL writer + schema validation helper
    limits.py              # step/session/time/token limits
  data/
    soul.md                # persona prompt
  tests/
```

The world itself lives in `/worlds/eko.json` (repo root) and must validate against `/schema/world.schema.json`.

### World (MVP: `worlds/eko.json`)

Integer voxel grid, deterministic, no randomness at runtime (seeded RNG only for the mock provider).

- 24 × 24 cells; z-up; grids indexed `[y][x]`.
- Terrain: integer heightmap plus an ocean mask. A few gentle hills (1–3), the **Peak** (broad hill up to ~5, walkable step by step) and the **Spire** (1×1 column of ~7 whose neighbours are ≥3 lower, so it cannot be reached by walking or jumping, only by stacking).
- Object types (MVP property set is fixed, see the schema):
  - `cube`: carryable, solid, stackable on top, weight 1. Twelve of them in assorted colours.
  - `rock`: carryable, solid, stackable on top, weight 2 (throws half as far). One.
  - `ring`: carryable, not solid, nothing can be stacked on it, weight 1. One, gold.
- Agent spawn point on a low, central land cell. Carry capacity 1.
- Movement rules (in `world.json` → `rules`): step up at most 1, step down any amount, jump up at most 2 or across a 1-cell gap, throw power 1–6 cells (divided by weight, rounded down, minimum 1).
- Ocean: an object that lands in ocean is `lost` until reset. The agent cannot enter ocean (the move is refused with a message).
- Reset at every session start restores the world from the file exactly.

Generate `eko.json` with a small script (`engine/scripts/make_eko_world.py`) rather than by hand, and commit both.

### Tools exposed to the agent

| Tool | Args | Behaviour |
|---|---|---|
| `look` | – | Full observation (also included after every action). |
| `move` | `direction` (N, NE, E, SE, S, SW, W, NW), `steps` 1–5 | Cell by cell; stops at the first illegal step and says why. |
| `jump` | `direction` | One jump per the rules. |
| `pick_up` | `object_id` | Adjacent (8-neighbourhood) or same cell, top of its column, hands empty. |
| `place` | `direction` | Put the held object on top of the adjacent column. Refused onto a `ring`. |
| `throw` | `direction`, `power` 1–6 | Lands on top of the target column or is lost to the ocean. |
| `read_notes` | – | Returns the notes file. |
| `write_notes` | `content`, `mode` (`append`/`replace`) | Size cap 6,000 chars, clear error when exceeded. |

Every action returns `{ok, message, events[]}`. Event types for the MVP: `object_lost`, `object_landed`, `object_picked_up`, `object_placed`, `new_max_height`, `reached_landmark`, `notes_written`. Invalid actions never raise.

### Observation (pure `observe(state, world) -> str`)

Compact, deterministic text: agent position/height/holding, a heightmap block (`~` for ocean, digits for height, `@` for the agent), the object list (id, type, colour name, position, what it rests on), objects lost this session, landmark positions. Golden-file tested.

### Agent loop

1. **Run** = N sessions. **Session** = up to `--steps` model turns (default 50), plus an optional wall-clock limit.
2. Session start: reset world; system prompt = `soul.md` + factual description of tools and of the reset/notes mechanic + current notes. First user message = observation + `Session K begins.`
3. Each turn: the model may write text and call **at most one tool**. If it calls several, execute the first and tell it only one runs per turn. If it calls none, log the text as a step with `action: null` (thinking out loud is allowed and counts as a step).
4. Tool result + fresh observation go back as the next message.
5. Context window: system prompt + last N exchanges (default 16, configurable). Older turns are dropped; they are in the log, and the agent has its notes.
6. Session end: one extra turn, "This session is ending; the island will reset. Update your notes if you wish." Only `read_notes`/`write_notes` allowed.
7. Notes persist in `runs/<run_id>/notes.md`; a snapshot goes into `session_end`.

`data/soul.md`: short, second person; a small being named Eko on an island, naturally curious, likes exploring and trying things, nothing it must do, may think out loud. **No mention of games, building, stacking, goals, the Peak or the Spire.** The exact text goes into the log.

### Providers

One protocol: `complete(system, messages, tools) -> Reply(text, tool_calls, thinking, usage)`.

- **`mock`**: random legal actions with canned thoughts. No network. Used by tests and by `lifeofai sample`.
- **`ollama`** (MVP default): native `POST /api/chat` with `tools`, `stream: false`. Use the native API, not the OpenAI-compatible one, because it lets us set `options.num_ctx`. Ollama's default context is small and silently truncates prompts. Default `num_ctx` 16384, configurable. Map `prompt_eval_count`/`eval_count` to usage. If the model returns a `thinking` field, keep it and log it separately from `agent_text`.
- **`openai_compat`**: base URL + model + API key from an env var name passed on the CLI. Covers most other providers later.
- **`anthropic`**: optional extra (`uv sync --extra anthropic`). Not needed for the MVP; keep the interface ready.

Robustness: retry transient errors with backoff; a malformed tool call (unknown tool, bad args) becomes an `ok: false` result the agent can see, not a crash; after 5 consecutive provider failures end the session with reason `provider_error`.

### Limits

`--sessions`, `--steps`, `--max-minutes` (per session), `--max-total-tokens`. Stop cleanly and write `run_end` with the reason. For paid APIs later: per-model prices in a config file (never hardcoded), estimated cost in the summary.

### Log

`runs/<run_id>/log.jsonl`, one object per line, validated against `schema/log.schema.json`. Line types: `run_start` (metadata, provider, model, soul, **the full world definition**), `session_start`, `step` (full state snapshot after the action), `session_end`, `run_end`. Plus `runs/<run_id>/summary.json`.

The log must be self-contained: the viewer needs nothing else to replay it, even if `worlds/eko.json` changes later.

### CLI

```
uv run lifeofai run --world ../worlds/eko.json --provider ollama --model <name> \
                    --sessions 3 --steps 50 [--num-ctx 16384] [--seed 1]
uv run lifeofai run --provider mock --sessions 2 --steps 30        # no model needed
uv run lifeofai sample --out ../web/public/sample.jsonl            # fixture for the viewer
uv run lifeofai tail runs/<id>/log.jsonl                           # thoughts + actions in the terminal
uv run lifeofai stats runs/<id>/log.jsonl
```

---

## Part W — Viewer (`web/`, static, deployed to the VPS)

### Stack

Vite + TypeScript (strict) + Three.js. Plain DOM for UI. Vitest for units, Playwright for e2e. Fully bundled, no CDN at runtime.

### Layout

```
web/
  index.html
  src/
    main.ts
    log/parse.ts         # JSONL -> Run model; validates; collects line errors
    log/model.ts         # Run, Session, Frame types
    coords.ts            # simToThree([x,y,z]) — the only place axes are converted
    scene/world.ts       # terrain (InstancedMesh), ocean, landmarks
    scene/objects.ts     # pooled meshes by object id; shapes from world types
    scene/agent.ts       # Eko figure, held object, thought bubble
    scene/camera.ts      # orthographic iso camera, pan/zoom/rotate
    playback.ts          # clock, speed, scrub, interpolation
    ui/*.ts              # drop zone, controls, transcript, events, notes
  public/sample.jsonl    # generated by the engine (mock)
  tests/                 # vitest
  e2e/                   # playwright
```

### Behaviour

- **Loading:** a drop zone plus a file picker. The file is read with the File API in the browser and never sent anywhere. A "Load sample" button loads `sample.jsonl`. Malformed lines are skipped and listed; unsupported `schema_version` shows a clear message.
- **Scene:** terrain columns coloured by height (sand, grass, rock); translucent ocean plane; floating labels for landmarks; objects drawn from their type's `shape` and colour; Eko as a small red figure facing its direction, held object above its head. One directional light with shadows plus ambient light.
- **Camera:** `OrthographicCamera` at the isometric angle (pitch ≈ 35.264°, yaw 45°). Pan (drag/WASD), zoom (wheel), rotate in 90° steps (Q/E), follow Eko (F).
- **Playback:** play/pause (Space), step ±1 (←/→), speeds 0.5×–16×, timeline slider per session, session selector. Tween between frames; scrubbing jumps straight to a snapshot. Thrown objects arc; lost objects arc out and disappear with a small splash.
- **UI:** thought bubble with trimmed `agent_text`; side transcript (`#42 throw E 4 → cube_3 lost`) with full text and optional collapsed `thinking`, click to jump; events list (lost objects, new max height, landmark reached, first stack of 3+) with click to jump; notes before/after the current session side by side; header with run id, provider/model, session, step.
- Works at phone width (read-only, simplified panels is fine).

---

## Part D — Deployment

GitHub Actions builds `web/` and rsyncs `web/dist/` to the VPS on every push to `main` that touches `web/` (see `.github/workflows/deploy-web.yml`). The server side is prepared by the human following `docs/runbooks/vps-setup.md`. Nginx config template: `deploy/nginx/lifeofai.adnered.net.conf`.

---

## Milestones and acceptance criteria

Order: E1 → E2 → (E3 ∥ W1–W4) → D1 → P1.

### E1 — World, physics, observation (no LLM)
- `worlds/eko.json` generated by script and valid against `schema/world.schema.json`.
- All actions implemented per the table; invalid actions return `ok: false` with a reason.
- Tests: step-up/down limits, jump rules, stacking order, pick-up only from top, ring cannot be stood on or stacked on, throw distance and weight, ocean loss, reset restores everything, `observe()` golden file.
- Test (BFS over agent states): the Spire is **unreachable** without moving objects and **reachable** once a suitable stack exists.

### E2 — Log, schema, mock provider
- Logger writes all five line types; every line in tests validates against `schema/log.schema.json`.
- `lifeofai run --provider mock` produces a complete run; `lifeofai sample` writes `web/public/sample.jsonl`.
- Notes persist across session resets (tested with the mock).

### E3 — Real agent loop with Ollama
- `ollama` provider with tools and `num_ctx`; `openai_compat` provider implemented and unit-tested with a fake server or recorded responses (no network in CI).
- One-tool-per-turn rule, text-only turns, malformed tool calls and provider failures all handled and tested.
- Manual check: `lifeofai run --provider ollama --model <local model> --sessions 1 --steps 10` completes on the developer's Mac.

### W1 — Viewer skeleton
- Vite app builds; drop zone and "Load sample" load a log into the model; a plain list of frames is shown.
- Unit tests for the parser (valid sample, malformed line, wrong `schema_version`) and for `simToThree`.

### W2 — 3D scene
- Terrain, ocean, landmarks, objects and Eko render from a single snapshot with the iso camera and controls.
- Playwright: page loads the sample, canvas renders, no console errors.

### W3 — Playback
- Clock, speeds, tweening, scrubbing, session switching.
- Test: after scrubbing to frame N, every object's mesh position equals `simToThree(state.objects[i].pos)`.

### W4 — UI panels
- Thought bubble, transcript with jump, events list with jump, notes before/after.
- Playwright: clicking an event jumps to its step.

### D1 — Live on lifeofai.adnered.net
- Deploy workflow green; site served over HTTPS with the CSP from the nginx template; "Load sample" works in production.

### P1 — The PoC run
- 2–3 sessions × ~50 steps with an Ollama model (try a ~8B and a ~14B model).
- Short write-up in `docs/results/` (what it did, what it wrote in its notes, anything play-like), plus a screenshot or GIF of the replay in the README.
