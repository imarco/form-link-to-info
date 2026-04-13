#!/usr/bin/env python3
"""
obsidian adapter — Copy report into an Obsidian vault folder.

Config:
  {
    "vault_path": "/path/to/vault",
    "target_folder": "inbox",        # relative to vault root
    "add_frontmatter": true           # add Obsidian-compatible frontmatter if missing
  }

If target_folder is not set, defaults to "inbox".
"""

import re
from pathlib import Path
from datetime import date
from base import load_config, read_report, log_output


def ensure_frontmatter(content: str, filename: str) -> str:
    """Add Obsidian frontmatter if not present."""
    if content.startswith("---"):
        return content

    title = filename.replace(".md", "").replace("-", " ").title()
    fm = f"""---
date: {date.today().isoformat()}
type: note
tags: [linky, research]
source: linky
---

"""
    return fm + content


def main():
    import sys
    report_path, config = load_config(sys.argv)

    vault_path = Path(config.get("vault_path", "")).expanduser()
    if not vault_path.exists():
        print(f"ERROR: Vault not found: {vault_path}", file=sys.stderr)
        sys.exit(1)

    target = config.get("target_folder", "inbox")
    dest_dir = vault_path / target
    dest_dir.mkdir(parents=True, exist_ok=True)

    add_fm = config.get("add_frontmatter", True)

    if report_path.is_dir():
        for f in report_path.glob("*.md"):
            content = f.read_text(encoding="utf-8")
            if add_fm:
                content = ensure_frontmatter(content, f.name)
            (dest_dir / f.name).write_text(content, encoding="utf-8")
        log_output("obsidian", f"{dest_dir}/ ({len(list(report_path.glob('*.md')))} files)", "OK")
    else:
        content = read_report(report_path)
        if add_fm:
            content = ensure_frontmatter(content, report_path.name)
        dest = dest_dir / report_path.name
        dest.write_text(content, encoding="utf-8")
        log_output("obsidian", str(dest), "OK")


if __name__ == "__main__":
    main()
