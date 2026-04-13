#!/usr/bin/env python3
"""
base.py — Output adapter base utilities for Linky.

All adapters follow the same contract:
  python3 adapter.py <report_path> [--config <config_json>]

  - report_path: path to the markdown report file (or directory for multi-file)
  - config_json: JSON string with adapter-specific settings

Exit codes:
  0 = success
  1 = error (print message to stderr)

Adapters should be idempotent — running twice with the same input produces the same result.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime


def load_config(argv):
    """Parse common CLI args: report_path and optional --config JSON."""
    if len(argv) < 2:
        print(f"Usage: {argv[0]} <report_path> [--config '<json>']", file=sys.stderr)
        sys.exit(1)

    report_path = Path(argv[1])
    config = {}

    if "--config" in argv:
        idx = argv.index("--config")
        if idx + 1 < len(argv):
            config = json.loads(argv[idx + 1])

    return report_path, config


def read_report(report_path: Path) -> str:
    """Read a markdown report file."""
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}", file=sys.stderr)
        sys.exit(1)
    return report_path.read_text(encoding="utf-8")


def log_output(adapter_name: str, destination: str, status: str):
    """Print a structured log line for the skill to capture."""
    ts = datetime.now().isoformat(timespec="seconds")
    print(f"[{ts}] {adapter_name} → {destination}: {status}")
