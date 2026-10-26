#!/usr/bin/env python3
"""Render shields.io endpoint badges from docs/live-stats.json (no deps)."""
import json
import pathlib

root = pathlib.Path(__file__).resolve().parent.parent
stats = json.loads((root / "docs" / "live-stats.json").read_text())
services = stats.get("services", [])
counters = stats.get("counters", {})

up = sum(1 for s in services if s.get("status") == "up")
total = len(services)
all_up = total > 0 and up == total

badges = {
    "badge-stack.json": {
        "schemaVersion": 1,
        "label": "stack",
        "message": f"{up}/{total} services up",
        "color": "brightgreen" if all_up else "orange" if up else "red",
    },
    "badge-leads.json": {
        "schemaVersion": 1,
        "label": "leads scored",
        "message": str(counters.get("total_vectors", 0)) if False else str(counters.get("leads_scored", 0)),
        "color": "blue",
    },
    "badge-latency.json": {
        "schemaVersion": 1,
        "label": "gate latency",
        "message": f"{counters.get('avg_gate_latency_ms', '—')} ms",
        "color": "brightgreen" if (counters.get("avg_gate_latency_ms") or 99) < 100 else "yellow",
    },
    "badge-vectors.json": {
        "schemaVersion": 1,
        "label": "vectors",
        "message": f"{counters.get('total_vectors', 0)} @ 1536-dim",
        "color": "purple",
    },
}

for name, payload in badges.items():
    (root / "docs" / name).write_text(json.dumps(payload))
    print(f"{name}: {payload['message']}")
