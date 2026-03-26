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

def fetch_and_extract(url: str, max_chars: int = 30000) -> str:
    """使用 Scrapling 抓取页面，html2text 转为 Markdown。"""
    try:
        from scrapling import Fetcher
    except ImportError:
        print("ERROR: scrapling 未安装。请运行: pip install scrapling", file=sys.stderr)
        sys.exit(1)

    try:
        import html2text
    except ImportError:
        print("ERROR: html2text 未安装。请运行: pip install html2text", file=sys.stderr)
        sys.exit(1)

    # 抓取页面
    fetcher = Fetcher()
    page = fetcher.get(url)

    # 按优先级尝试正文选择器
    selectors = ["article", "main", ".post-content", "[class*='body']", "#content", ".content"]
    element = None
    for sel in selectors:
        try:
            found = page.css(sel)
            if found:
                element = found[0]
                break
        except Exception:
            continue

    # 如果没找到正文容器，用整个 body
    if element is None:
        try:
            body = page.css("body")
            if body:
                element = body[0]
        except Exception:
            pass

    if element is None:
        print("ERROR: 无法提取页面内容", file=sys.stderr)
        sys.exit(1)

    # 用 html2text 转换为 Markdown（保留链接和图片）
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # 不自动折行
    h.skip_internal_links = True
    h.inline_links = True

    md = h.handle(element.html_content)

    # 截断到指定字符数
    if len(md) > max_chars:
        md = md[:max_chars] + "\n\n[... 内容已截断，共 " + str(len(md)) + " 字符 ...]"

    return md


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 30000

    result = fetch_and_extract(url, max_chars)
    print(result)


if __name__ == "__main__":
    main()
