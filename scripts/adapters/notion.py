#!/usr/bin/env python3
"""
notion adapter — Prepare Notion-ready JSON from a report.

This adapter does NOT call the Notion API directly (that's done via MCP tools).
Instead, it transforms the report into structured JSON that the skill can feed
to the Notion MCP's create-page or create-database-row tools.

Config:
  {
    "database_id": "abc123...",
    "page_parent_id": "def456...",   # alternative: create as sub-page
    "output_json": "/tmp/linky-notion-payload.json"
  }

Output: writes a JSON file with Notion-compatible block structure.
The skill reads this file and passes it to the Notion MCP.
"""

import json
import re
from pathlib import Path
from base import load_config, read_report, log_output


def markdown_to_notion_blocks(md: str) -> list:
    """Convert markdown to simplified Notion block list.

    This is intentionally simple — handles headings, paragraphs, bullets, and code.
    The Notion MCP handles the actual API formatting.
    """
    blocks = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"type": "code", "language": lang, "content": "\n".join(code_lines)})
            i += 1
            continue

        # Headings
        if line.startswith("### "):
            blocks.append({"type": "heading_3", "content": line[4:]})
        elif line.startswith("## "):
            blocks.append({"type": "heading_2", "content": line[3:]})
        elif line.startswith("# "):
            blocks.append({"type": "heading_1", "content": line[2:]})
        # Bullets
        elif line.startswith("- "):
            blocks.append({"type": "bulleted_list_item", "content": line[2:]})
        # Non-empty paragraph
        elif line.strip():
            blocks.append({"type": "paragraph", "content": line})

        i += 1

    return blocks


def extract_title(md: str) -> str:
    """Extract first H1 as title."""
    for line in md.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return "Linky Research Report"


def main():
    import sys
    report_path, config = load_config(sys.argv)

    content = read_report(report_path)
    title = extract_title(content)
    blocks = markdown_to_notion_blocks(content)

    payload = {
        "title": title,
        "database_id": config.get("database_id", ""),
        "page_parent_id": config.get("page_parent_id", ""),
        "blocks": blocks,
    }

    output_path = Path(config.get("output_json", "/tmp/linky-notion-payload.json"))
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    log_output("notion", str(output_path), f"OK (prepared {len(blocks)} blocks)")


if __name__ == "__main__":
    main()
