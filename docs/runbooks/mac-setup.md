# Runbook — local machine setup (macOS, Apple Silicon)

Target: MacBook Pro M4, 16 GB RAM. The implementing agent may run these steps in the terminal **with the owner's approval for each install**. Nothing here touches the VPS.

Legend: **[AGENT]** the agent can do it · **[HUMAN]** the owner does it or confirms it.

## 1. Tools

**[AGENT]** Check what is already installed, install only what is missing:

```bash
command -v brew uv node gh ollama direnv
brew install uv node gh direnv          # only the missing ones
brew install ollama                     # or the Ollama.app from ollama.com — pick one, not both
```

Expected: `uv`, `node` (LTS), `gh`, `direnv` and `ollama` on PATH. `direnv` is already configured in `~/.zshrc` for this repo (`.envrc` loads `.env` with `GH_TOKEN`); do not modify `.env` or `.envrc`.

## 2. Ollama running natively

**[AGENT]**
```bash
ollama --version
curl -s http://localhost:11434/api/version || brew services start ollama
curl -s http://localhost:11434/api/version
```

Ollama must run natively (not in Docker): see `docs/decisions/0002-no-containers-in-mvp.md`.

## 3. Models

**[HUMAN]** chooses, **[AGENT]** pulls.

Requirements: the model must support **tool calling** (models tagged *tools* in the Ollama library). With 16 GB RAM, aim for:
- one model of roughly **7–8B** parameters (fast, for development), and
- one of roughly **12–14B** (smarter, for the real PoC run),

both in the default 4-bit quantisation. Leave headroom: the context window (`num_ctx` 16384) also costs memory.

```bash
ollama pull <model-8b>
ollama pull <model-14b>
ollama list
```

## 4. Tool-calling smoke test

**[AGENT]** No dependencies needed (standard library only):

```bash
python3 scripts/check_ollama_tools.py <model-8b>
python3 scripts/check_ollama_tools.py <model-14b>
```

Expected output ends with `PASS`: the model called the `move` tool with a valid direction. A `FAIL` means the model does not do tool calling reliably; pick another.

Record the chosen model names and their results in `docs/results/models.md`.

## 5. Optional, later (FVP builder)

The world builder (served from lifeofai.adnered.net) will call the local Ollama from the browser. That needs:

```bash
launchctl setenv OLLAMA_ORIGINS "https://lifeofai.adnered.net"   # then restart Ollama
```

Do **not** do this in the MVP.
