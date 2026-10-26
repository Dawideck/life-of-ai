# 0004 — Ollama (native API) is the default provider

**Status:** Accepted (2026-10-25)

**Context.** Experiments run locally on a MacBook Pro M4 with 16 GB RAM, so models of roughly 7–14B parameters (quantised) are practical. Other AI providers should be pluggable. Ollama's OpenAI-compatible endpoint does not expose the context-length option, and Ollama's default context is small enough to truncate our prompts silently.

**Decision.** The default provider calls Ollama's native `/api/chat` with tools and an explicit `options.num_ctx` (default 16384). An `openai_compat` provider covers other APIs. An `anthropic` provider is an optional extra. A `mock` provider exists for tests and fixtures.

**Consequences.** Model choice is limited to models with tool-calling support. Smaller models will make more malformed tool calls, so the engine must handle them gracefully (they are data, not errors).
