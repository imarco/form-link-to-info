#!/usr/bin/env python3
"""
scrapling_fetch.py — 使用 Scrapling + html2text 提取网页正文

用法：
    python3 scrapling_fetch.py <url> [max_chars]

参数：
    url         要提取的网页 URL
    max_chars   最大字符数（默认 30000）

输出：
    干净的 Markdown 格式正文

依赖安装：
    pip install scrapling html2text
"""

import sys
from pathlib import Path

def fetch_and_extract(url: str, max_chars: int = 30000) -> str:
    """使用 Scrapling 抓取页面，html2text 转为 Markdown。

    Compatibility wrapper: the implementation lives in scripts/linky so the
    Skill and local tests share one extractor path.
    """
    from linky.providers.scrapling import fetch_and_extract as _fetch_and_extract
    from linky.strategy import load_strategy

    strategy_path = Path(__file__).resolve().parents[1] / "references" / "fetch-strategy.toml"
    strategy = load_strategy(strategy_path)
    return _fetch_and_extract(url, max_chars, strategy)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__)
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    url = sys.argv[1]
    max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 30000

    try:
        result = fetch_and_extract(url, max_chars)
        print(result)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
