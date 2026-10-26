# 0003 — Log contains full state snapshots and is self-contained

**Status:** Accepted (2026-10-25)

**Context.** The viewer could either re-simulate from the initial world plus actions, or draw stored snapshots. Re-simulation requires identical physics in Python and TypeScript; any divergence produces a replay that silently lies.

**Decision.** Every `step` line carries the complete state after the action. `run_start` embeds the full world definition (terrain, types, objects, rules), so a log replays correctly even after `worlds/*.json` changes.

**Consequences.** Larger logs (still small: dozens of objects × a few hundred steps is a few MB). Scrubbing to any frame is trivial. The viewer contains no physics. The same line format can be streamed live later without changes.
