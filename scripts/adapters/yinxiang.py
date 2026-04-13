#!/usr/bin/env python3
"""
yinxiang (Evernote) adapter — Convert report to ENML and call Yinxiang API.

Config:
  {
    "token": "...",                    # Yinxiang developer token
    "notebook": "Research",            # target notebook name
    "sandbox": false,                  # use sandbox API
    "tags": ["linky", "research"]      # tags to add
  }

Dependencies:
  pip install evernote3 markdown

If evernote3 SDK is not available, falls back to generating an .enex file
that can be manually imported.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from base import load_config, read_report, log_output


def markdown_to_enml(md: str) -> str:
    """Convert markdown to ENML (Evernote Markup Language).

    ENML is a subset of XHTML. We do a simple conversion.
    """
    try:
        import markdown
        html = markdown.markdown(md, extensions=["tables", "fenced_code"])
    except ImportError:
        # Fallback: wrap in pre tag
        import html as html_mod
        html = f"<pre>{html_mod.escape(md)}</pre>"

    enml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>{html}</en-note>"""
    return enml


def export_enex(title: str, enml: str, tags: list, output_path: Path):
    """Generate .enex file for manual import."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    tag_xml = "".join(f"<tag>{t}</tag>" for t in tags)

    enex = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export4.dtd">
<en-export>
<note>
<title>{title}</title>
<content><![CDATA[{enml}]]></content>
<created>{ts}</created>
{tag_xml}
</note>
</en-export>"""

    output_path.write_text(enex, encoding="utf-8")


def main():
    report_path, config = load_config(sys.argv)
    content = read_report(report_path)
    tags = config.get("tags", ["linky", "research"])

    # Extract title from first heading
    title = "Linky Research Report"
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break

    enml = markdown_to_enml(content)

    # Try Evernote SDK first
    token = config.get("token")
    if token:
        try:
            from evernote.api.client import EvernoteClient
            sandbox = config.get("sandbox", False)
            china = not sandbox  # Yinxiang uses China service
            client = EvernoteClient(token=token, china=china, sandbox=sandbox)
            note_store = client.get_note_store()

            # Find notebook
            notebook_name = config.get("notebook", "Research")
            notebooks = note_store.listNotebooks()
            nb = next((n for n in notebooks if n.name == notebook_name), None)

            from evernote.edam.type.ttypes import Note
            note = Note()
            note.title = title
            note.content = enml
            if nb:
                note.notebookGuid = nb.guid
            note.tagNames = tags

            created = note_store.createNote(note)
            log_output("yinxiang", f"notebook:{notebook_name}", f"OK (guid: {created.guid})")
            return
        except Exception as e:
            print(f"WARNING: SDK failed ({e}), falling back to .enex export", file=sys.stderr)

    # Fallback: generate .enex file
    output_path = Path(f"/tmp/linky-{datetime.now().strftime('%Y%m%d-%H%M%S')}.enex")
    export_enex(title, enml, tags, output_path)
    log_output("yinxiang", str(output_path), "OK (enex file, import manually)")


if __name__ == "__main__":
    main()
