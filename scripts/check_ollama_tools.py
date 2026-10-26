#!/usr/bin/env python3
"""Smoke test: does a local Ollama model call tools reliably?

Usage:
    python3 scripts/check_ollama_tools.py <model> [--host http://localhost:11434] [--tries 3]

Standard library only, so it works before the engine project exists.
Prints PASS if the model called `move` with a valid direction in every try.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "move",
            "description": "Walk in a direction for a number of cells.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": DIRECTIONS},
                    "steps": {"type": "integer", "minimum": 1, "maximum": 5},
                },
                "required": ["direction", "steps"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pick_up",
            "description": "Pick up an adjacent object by id.",
            "parameters": {
                "type": "object",
                "properties": {"object_id": {"type": "string"}},
                "required": ["object_id"],
            },
        },
    },
]

SYSTEM = (
    "You are Eko, a small curious being on an island. You act only by calling tools. "
    "Call exactly one tool per turn."
)
USER = (
    "You are at (5, 5). A red cube (cube_1) lies at (8, 5), three cells to the east. "
    "Walk next to it."
)


def chat(host: str, model: str) -> dict:
    body = {
        "model": model,
        "stream": False,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER}],
        "tools": TOOLS,
        "options": {"num_ctx": 4096, "temperature": 0.7},
    }
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def check(reply: dict) -> tuple[bool, str]:
    calls = (reply.get("message") or {}).get("tool_calls") or []
    if not calls:
        text = (reply.get("message") or {}).get("content", "")[:200]
        return False, f"no tool call (text: {text!r})"
    fn = calls[0].get("function", {})
    name, args = fn.get("name"), fn.get("arguments")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            return False, f"arguments not JSON: {args!r}"
    if name != "move":
        return False, f"called {name!r} instead of 'move' with {args}"
    if not isinstance(args, dict) or args.get("direction") not in DIRECTIONS:
        return False, f"invalid direction in {args}"
    extra = f" (+{len(calls) - 1} extra call(s))" if len(calls) > 1 else ""
    return True, f"move {args}{extra}"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--host", default="http://localhost:11434")
    p.add_argument("--tries", type=int, default=3)
    a = p.parse_args()

    ok_all = True
    for i in range(1, a.tries + 1):
        t0 = time.monotonic()
        try:
            reply = chat(a.host, a.model)
        except urllib.error.URLError as e:
            print(f"Cannot reach Ollama at {a.host}: {e}")
            return 2
        ok, detail = check(reply)
        ok_all &= ok
        secs = time.monotonic() - t0
        print(f"try {i}: {'ok  ' if ok else 'bad '} {detail}  [{secs:.1f}s]")
    print("PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
