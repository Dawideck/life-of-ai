# Roadmap after the MVP (FVP and beyond)

Nothing here is started until the MVP's definition of done is met. Order is a suggestion, not a commitment.

## 1. World builder (in `web/`)

A browser tool for defining worlds, sharing the renderer with the viewer.

- **Level 1: placement.** Paint terrain height and ocean with a brush, place objects of existing types, set the agent spawn, export/import `world.json`. Validation against `schema/world.schema.json` before export.
- **Level 2: custom types.** "Add element": name, description, shape, colour, plus toggles/sliders generated **from the schema** (carryable, solid, stackable, weight, …). The builder hardcodes no property names; a new property in the schema appears in the UI automatically.
- **Level 4: describe it.** Type a description ("an old wooden barrel, floats, you can put things in it"); a **local** model (the browser calls the user's own Ollama at `localhost:11434`, with `OLLAMA_ORIGINS` set) proposes property values from the schema; the user reviews and confirms. Properties the engine cannot express are reported, not invented. The LLM helps only at authoring time; at run time the rules stay in code.
- **Test button:** run a few mock-agent steps against the edited world (needs a tiny local helper, or a JS port of the physics; decide then).

## 2. Engine mechanics (each one: schema + engine rule + viewer support + tests)

- **Level 3: event rules.** A small `when / if / then` vocabulary in `world.json` (e.g. *when* an object touches water *if* not `floats` *then* it is lost; *when* struck *then* emit a note of pitch X).
- Candidates: floating and drifting, containers, sound-making objects (music-themed world), day/night, growth over time (garden world), limited visibility (cave world).

## 3. Publishing runs to the server (with auth)

- `lifeofai publish runs/<id>` uploads a log with rsync over SSH, using the same restricted deploy user, into `/var/www/lifeofai/runs/<id>/`, and updates `runs/index.json`.
- The viewer gets a run gallery.
- Viewing published runs is protected by nginx basic auth (or Cloudflare Access). **Nothing is ever uploaded through the website**; the site stays static and read-only.

## 4. Experiments and evaluation

- Compare models (local sizes and families, later paid APIs) on the same world and soul.
- Soul ablation: curious persona vs neutral persona as a control.
- Task evaluation as in the paper: agents with island experience (and their notes) vs fresh agents on concrete tasks ("put a cube on the Spire", "bring the ring to the Peak").
- Live mode: stream the same JSON lines over WebSocket from the local engine to the viewer opened on the same machine.
