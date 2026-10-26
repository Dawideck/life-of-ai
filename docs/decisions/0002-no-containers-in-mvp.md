# 0002 — No containers in the MVP

**Status:** Accepted (2026-10-25)

**Context.** Docker on macOS cannot use the Apple GPU (Metal), so Ollama in a container would run on CPU and be dramatically slower. The Python engine is isolated by `uv` already. The web app is static files served by an nginx that already runs on the VPS.

**Decision.** Ollama runs natively. The engine runs with `uv`. The site is deployed as files into `/var/www/lifeofai`. No Dockerfiles or compose files in the MVP.

**Revisit when** any long-running server process is added (e.g. a run gallery with a backend), or when the engine needs to run on another machine reproducibly.
