#!/usr/bin/env python3
"""
Custom API adapter template — Copy and modify for your API.

This template shows the contract every adapter must follow.
Save your customized version to ~/.config/linky/output-adapters/my-api.py

Config example:
  {
    "endpoint": "https://api.example.com/notes",
    "api_key": "...",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body_template": {"title": "{title}", "content": "{content}"}
  }
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from base import load_config, read_report, log_output


def main():
    import sys
    report_path, config = load_config(sys.argv)

    endpoint = config.get("endpoint")
    if not endpoint:
        print("ERROR: 'endpoint' is required in config", file=sys.stderr)
        sys.exit(1)

    content = read_report(report_path)
    title = report_path.stem.replace("-", " ").title()

    # Build request body from template
    body_tpl = config.get("body_template", {"title": "{title}", "content": "{content}"})
    body = json.dumps(body_tpl).replace('"{title}"', json.dumps(title)).replace('"{content}"', json.dumps(content))

    headers = config.get("headers", {"Content-Type": "application/json"})
    api_key = config.get("api_key")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    method = config.get("method", "POST")
    req = urllib.request.Request(endpoint, data=body.encode("utf-8"), headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            log_output("custom-api", endpoint, f"OK ({resp.status})")
    except urllib.error.HTTPError as e:
        print(f"ERROR: API returned {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
