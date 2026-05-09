from __future__ import annotations

import re
from typing import Any


BLOCKED_PATTERNS = [
    "login",
    "sign in",
    "sign up",
    "register",
    "captcha",
    "验证码",
    "登录",
    "注册",
    "权限",
    "403",
    "401",
]


def score_markdown(markdown: str) -> dict[str, Any]:
    text = (markdown or "").strip()
    lower = text.lower()
    reasons: list[str] = []

    if not text:
        return {"score": 0.0, "status": "failed", "reasons": ["empty"]}

    length = len(text)
    score = min(length / 1200.0, 0.45)
    if length < 160:
        reasons.append("short_content")

    if re.search(r"^#{1,3}\s+", text, flags=re.MULTILINE):
        score += 0.15
    else:
        reasons.append("missing_heading")

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 40]
    if len(paragraphs) >= 3:
        score += 0.2
    else:
        reasons.append("few_paragraphs")

    if "[" in text and "](" in text:
        score += 0.1

    if re.search(r"\b(source|author|date|published|updated)\b", lower):
        score += 0.1

    blocked = [pattern for pattern in BLOCKED_PATTERNS if pattern in lower]
    if blocked:
        reasons.append("possible_login_or_blocked_page")
        score = min(score, 0.3)

    score = round(min(score, 1.0), 3)
    if blocked:
        status = "blocked"
    elif score >= 0.55:
        status = "success"
    elif text:
        status = "partial"
    else:
        status = "failed"

    return {"score": score, "status": status, "reasons": reasons}
