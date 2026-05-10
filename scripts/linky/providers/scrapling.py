from __future__ import annotations

from urllib.parse import urlparse
from typing import Any


DEFAULT_SELECTORS = ["article", "main", ".post-content", "[class*='body']", "#content", ".content"]


def selectors_for_url(url: str, strategy: dict[str, Any] | None = None) -> list[str]:
    if not strategy:
        return DEFAULT_SELECTORS

    domain = urlparse(url).netloc.lower().removeprefix("www.")
    scrapling = strategy.get("scrapling", {})
    domain_selectors = scrapling.get("domain_selectors", {})
    for pattern, selectors in domain_selectors.items():
        normalized = pattern.lower().removeprefix("www.")
        if domain == normalized or domain.endswith("." + normalized):
            return list(selectors)
    return list(scrapling.get("selectors", DEFAULT_SELECTORS))


def fetch_and_extract(url: str, max_chars: int = 30000, strategy: dict[str, Any] | None = None) -> str:
    try:
        from scrapling import Fetcher
    except ImportError as exc:
        raise RuntimeError("scrapling 未安装。请运行: pip install scrapling") from exc

    try:
        import html2text
    except ImportError as exc:
        raise RuntimeError("html2text 未安装。请运行: pip install html2text") from exc

    fetcher = Fetcher()
    page = fetcher.get(url)

    element = None
    for selector in selectors_for_url(url, strategy):
        try:
            found = page.css(selector)
            if found:
                element = found[0]
                break
        except Exception:
            continue

    if element is None:
        try:
            body = page.css("body")
            if body:
                element = body[0]
        except Exception:
            pass

    if element is None:
        raise RuntimeError("无法提取页面内容")

    html_config = (strategy or {}).get("html2text", {})
    converter = html2text.HTML2Text()
    converter.ignore_links = bool(html_config.get("ignore_links", False))
    converter.ignore_images = bool(html_config.get("ignore_images", False))
    converter.body_width = int(html_config.get("body_width", 0))
    converter.skip_internal_links = bool(html_config.get("skip_internal_links", True))
    converter.inline_links = bool(html_config.get("inline_links", True))

    markdown = converter.handle(element.html_content)
    if len(markdown) > max_chars:
        return markdown[:max_chars] + f"\n\n[... 内容已截断，共 {len(markdown)} 字符 ...]"
    return markdown
