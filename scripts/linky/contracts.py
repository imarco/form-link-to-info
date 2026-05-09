from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class ExtractionAttempt:
    provider: str
    status: str
    elapsed_ms: int
    content_length: int = 0
    error: str | None = None
    fallback_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExtractionTrace:
    url: str
    attempts: list[ExtractionAttempt] = field(default_factory=list)
    final_provider: str | None = None
    final_status: str = "failed"
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str | None = None
    quality_score: float = 0.0

    def finish(self, provider: str | None, status: str, quality_score: float) -> None:
        self.final_provider = provider
        self.final_status = status
        self.quality_score = round(float(quality_score), 3)
        self.finished_at = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["attempts"] = [attempt.to_dict() for attempt in self.attempts]
        return data


@dataclass
class ExtractionResult:
    url: str
    status: str
    provider: str | None
    markdown: str
    metadata: dict[str, Any] = field(default_factory=dict)
    quality: dict[str, Any] = field(default_factory=dict)
    trace: ExtractionTrace | None = None
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "provider": self.provider,
            "markdown": self.markdown,
            "metadata": self.metadata,
            "quality": self.quality,
            "trace": self.trace.to_dict() if self.trace else None,
            "errors": self.errors,
        }
