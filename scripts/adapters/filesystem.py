#!/usr/bin/env python3
"""
filesystem adapter — Copy report to a local directory.

Config:
  {"output_dir": "/path/to/dir", "filename": "optional-name.md"}

If output_dir is not set, uses ~/Documents/linky-reports/
"""

import shutil
from pathlib import Path
from base import load_config, read_report, log_output


def main():
    report_path, config = load_config(__import__("sys").argv)

    output_dir = Path(config.get("output_dir", "~/Documents/linky-reports")).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = config.get("filename", report_path.name)
    dest = output_dir / filename

    if report_path.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(report_path, dest)
    else:
        shutil.copy2(report_path, dest)

    log_output("filesystem", str(dest), "OK")


if __name__ == "__main__":
    main()
