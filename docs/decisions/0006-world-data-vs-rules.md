# 0006 — Worlds are data; behaviour is code

**Status:** Accepted (2026-10-25)

**Context.** We want users to define worlds (eventually through a builder, even by describing objects in words), but we also want a world that resists the agent consistently, instead of an LLM judging what "should" happen.

**Decision.** `world.json` describes what exists: terrain, object types with a **fixed, schema-defined property set**, object instances, agent spawn and numeric rules. What those properties mean is implemented in the engine. Free-text `description` fields are shown to the agent and the viewer only; the engine never interprets them. A property without an engine rule must not exist in the schema.

**Consequences.** Every new mechanic is a coordinated change: schema + engine rule + viewer + tests. The builder can generate its forms from the schema. Runs are deterministic and reproducible.
