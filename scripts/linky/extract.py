from __future__ import annotations

import time
import urllib.request
from pathlib import Path
from typing import Any, Callable

from .contracts import ExtractionAttempt, ExtractionResult, ExtractionTrace
from .quality import score_markdown
from .strategy import load_strategy, provider_config, quality_threshold, resolve_provider_chain

ProviderFn = Callable[[str, dict[str, Any], dict[str, Any]], dict[str, Any] | str]


def _http_markdown(url: str, provider: dict[str, Any], strategy: dict[str, Any]) -> str:
    max_chars = int(strategy.get("global", {}).get("max_chars", 30000))
    pattern = provider.get("url_pattern", "{url}")
    target = pattern.replace("{url}", url)
    with urllib.request.urlopen(target, timeout=int(strategy.get("global", {}).get("timeout_seconds", 15))) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    return text[:max_chars]


def _trafilatura_provider(url: str, provider: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
    try:
        import trafilatura
    except ImportError as exc:
        raise RuntimeError("trafilatura 未安装。请运行: pip install trafilatura") from exc

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise RuntimeError("trafilatura fetch_url returned empty content")
    markdown = trafilatura.extract(downloaded, output_format="markdown", include_links=True, include_images=True)
    if not markdown:
        raise RuntimeError("trafilatura extract returned empty content")
    return {"markdown": markdown, "metadata": {"provider": "trafilatura"}}


def _scrapling_provider(url: str, provider: dict[str, Any], strategy: dict[str, Any]) -> dict[str, Any]:
    from .providers.scrapling import fetch_and_extract

    markdown = fetch_and_extract(url, int(strategy.get("global", {}).get("max_chars", 30000)), strategy)
    return {"markdown": markdown, "metadata": {"provider": "scrapling"}}


BUILTIN_PROVIDERS: dict[str, ProviderFn] = {
    "jina": lambda url, provider, strategy: {"markdown": _http_markdown(url, provider, strategy), "metadata": {}},
    "webfetch": lambda url, provider, strategy: {"markdown": _http_markdown(url, provider, strategy), "metadata": {}},
    "trafilatura": _trafilatura_provider,
    "scrapling": _scrapling_provider,
}


def extract_url(
    url: str,
    strategy_path: str | Path | None = None,
    strategy: dict[str, Any] | None = None,
    providers: dict[str, ProviderFn] | None = None,
) -> ExtractionResult:
    if strategy is None:
        if strategy_path is None:
            strategy_path = Path(__file__).resolve().parents[2] / "references" / "fetch-strategy.toml"
        strategy = load_strategy(strategy_path)

    provider_fns = dict(BUILTIN_PROVIDERS)
    if providers:
        provider_fns.update(providers)

    trace = ExtractionTrace(url=url)
    threshold = quality_threshold(strategy)
    errors: list[str] = []
    best_markdown = ""
    best_provider: str | None = None
    best_quality = {"score": 0.0, "status": "failed", "reasons": ["not_attempted"]}
    best_metadata: dict[str, Any] = {}

    for provider_id in resolve_provider_chain(url, strategy):
        provider = provider_config(strategy, provider_id)
        fn = provider_fns.get(provider_id)
        start = time.monotonic()
        if not fn:
            message = f"provider not implemented: {provider_id}"
            errors.append(message)
            trace.attempts.append(
                ExtractionAttempt(provider=provider_id, status="failed", elapsed_ms=0, error=message)
            )
            continue

        try:
            raw = fn(url, provider, strategy)
            if isinstance(raw, str):
                markdown = raw
                metadata: dict[str, Any] = {}
            else:
                markdown = str(raw.get("markdown", ""))
                metadata = dict(raw.get("metadata", {}))

            quality = score_markdown(markdown)
            elapsed_ms = int((time.monotonic() - start) * 1000)
            fallback_reason = None if quality["score"] >= threshold else "low_quality"
            trace.attempts.append(
                ExtractionAttempt(
                    provider=provider_id,
                    status=quality["status"],
                    elapsed_ms=elapsed_ms,
                    content_length=len(markdown),
                    fallback_reason=fallback_reason,
                )
            )

            if quality["score"] > float(best_quality.get("score", 0.0)):
                best_markdown = markdown
                best_provider = provider_id
                best_quality = quality
                best_metadata = metadata

            if quality["score"] >= threshold and quality["status"] == "success":
                trace.finish(provider_id, "success", quality["score"])
                return ExtractionResult(
                    url=url,
                    status="success",
                    provider=provider_id,
                    markdown=markdown,
                    metadata=metadata,
                    quality=quality,
                    trace=trace,
                    errors=errors,
                )
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            message = str(exc)
            errors.append(f"{provider_id}: {message}")
            trace.attempts.append(
                ExtractionAttempt(provider=provider_id, status="failed", elapsed_ms=elapsed_ms, error=message)
            )

    final_status = str(best_quality.get("status", "failed"))
    if best_markdown and final_status == "success":
        final_status = "partial"
    trace.finish(best_provider, final_status, float(best_quality.get("score", 0.0)))
    return ExtractionResult(
        url=url,
        status=final_status,
        provider=best_provider,
        markdown=best_markdown,
        metadata=best_metadata,
        quality=best_quality,
        trace=trace,
        errors=errors,
    )
