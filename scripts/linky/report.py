from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ReportItem:
    name: str
    url: str
    type: str
    access_status: str
    one_line: str
    judgment: str
    next_action: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReportData:
    title: str
    items: list[ReportItem] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    conclusions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "items": [item.to_dict() for item in self.items],
            "summary": self.summary,
            "conclusions": self.conclusions,
        }

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", "## A. 研究总览", ""]
        lines.append(f"- 链接总数：{len(self.items)}")
        for key, value in self.summary.items():
            lines.append(f"- {key}：{value}")
        lines.extend(["", "## B. 分类型逐条整理", ""])

        for idx, item in enumerate(self.items, 1):
            lines.extend(
                [
                    f"### {idx}. {item.name}",
                    "",
                    f"- **链接**：{item.url}",
                    f"- **类型**：{item.type}",
                    f"- **访问状态**：{item.access_status}",
                    f"- **一句话结论**：{item.one_line}",
                    "",
                    "#### 我的判断",
                    f"- {item.judgment}",
                    "",
                    "#### 建议的后续行动",
                    f"- {item.next_action}",
                    "",
                ]
            )

        lines.extend(["## C. 研究结论", ""])
        if self.conclusions:
            lines.extend(f"- {item}" for item in self.conclusions)
        else:
            lines.append("- 暂无额外结论。")
        return "\n".join(lines).rstrip() + "\n"
