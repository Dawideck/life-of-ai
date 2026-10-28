# Local model tool-calling results

Ran via `scripts/check_ollama_tools.py <model>` on a MacBook Pro M4, 16 GB RAM,
Ollama 0.32.1, native (not containerized). Each run is 3 tries calling the
`move` tool; PASS requires a valid tool call on all 3.

| Model | Tier | Size (4-bit) | Result | Notes |
|---|---|---|---|---|
| `qwen2.5:7b` | 7-8B | 4.7 GB | FAIL | No tool call on any of 3 tries (empty text). |
| `qwen3:8b` | 7-8B | 5.2 GB | FAIL | Flaky: 2/3 tries ok, 1/3 empty text. |
| `llama3.1:8b` | 7-8B | ~4.9 GB | **PASS** | All 3 tries ok, ~1-8s each. |
| `qwen2.5:14b` | 12-14B | 9.0 GB | **PASS** | All 3 tries ok, ~2.5s each after warmup. |

## Chosen models

- **Fast / dev tier:** `llama3.1:8b`
- **Smarter / PoC tier:** `qwen2.5:14b`

`qwen2.5:7b` and `qwen3:8b` were rejected per the runbook's FAIL rule
(`docs/runbooks/mac-setup.md`, step 4) despite being tagged *tools* in the
Ollama library — tagging alone wasn't a reliable predictor here.
