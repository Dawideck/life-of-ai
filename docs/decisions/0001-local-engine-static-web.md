# 0001 — Engine runs only locally; the web app is static

**Status:** Accepted (2026-10-25)

**Context.** Agents run on local models (Ollama) on the developer's Mac, optionally on paid APIs later. The VPS (mikr.us, 2 GB RAM, nginx behind Cloudflare) is shared with other projects. The owner wants no way for anyone to push content onto the server.

**Decision.** The engine (world, physics, agent, providers) runs only on the local machine. The web app (viewer now, builder later) is a static site served by the existing nginx. In the MVP, logs are opened with drag & drop and never leave the user's browser. Later, logs are published from the local machine over SSH (rsync), never through the website.

**Consequences.** No server-side code, no database, negligible server RAM, a tiny attack surface. Live viewing and server-side features require a separate decision.
