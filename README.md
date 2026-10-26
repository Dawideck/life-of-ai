# life-of-ai

What does an AI agent do when nobody gives it a task?

**life-of-ai** is a small, local re-creation of MIT's "Eko" experiment (October 2026), in which language-model agents were left alone on a virtual island with no goals and no rewards, and began to do something that looked a lot like play.

Here, an agent running on a **local model (Ollama)** or any compatible AI API lives in a tiny voxel world. It sees the world only as text and acts through tools: move, jump, pick up, place, throw. It also keeps a notes file. The world resets every session, but the notes persist. Everything it does is recorded to a log, which you can then **replay as an isometric 3D animation in the browser**.

> Status: early MVP. It's not done until it ships.

## How it fits together

```
LOCAL (your machine)                              WEB (static, lifeofai.adnered.net)
┌──────────────────────────────┐                ┌─────────────────────────────┐
│ engine/  (Python)            │   log.jsonl    │ web/  (Vite + TS + Three.js)│
│  world + physics + agent     │ ─────────────► │  replay viewer (MVP)        │
│  providers: Ollama | API …   │  drag & drop   │  world builder (later)      │
└──────────────────────────────┘                └─────────────────────────────┘
```

- **engine/** — runs the experiment locally and writes `runs/<run_id>/log.jsonl`.
- **web/** — a static site that replays a log. The log is opened locally in the browser (drag & drop) and never uploaded anywhere.
- **schema/** — JSON Schemas for `world.json` and `log.jsonl`, the contract between engine and web.
- **worlds/** — world definitions. The MVP ships `eko.json`, modeled on the original island.
- **docs/** — plan, roadmap, decision records and runbooks.

## Quick start

Coming with the first milestones. See [`docs/PLAN-mvp.md`](docs/PLAN-mvp.md).

## Background

- MIT Technology Review, *AI researchers stranded Claude on a virtual desert island. It started to "play."* (Oct 2026)
- The original paper by Cloos, Norelli et al. (MIT) is on arXiv.

This project is an independent hobby re-creation and is not affiliated with MIT or the original authors.
