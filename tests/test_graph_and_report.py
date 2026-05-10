import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from linky.graph import ResearchGraph
from linky.report import ReportData, ReportItem


class GraphAndReportTests(unittest.TestCase):
    def test_research_graph_deduplicates_nodes_and_edges(self):
        graph = ResearchGraph()
        graph.add_node("topic:agents", "topic", "Agents", {"count": 1})
        graph.add_node("topic:agents", "topic", "Agents", {"last_seen": "today"})
        graph.add_node("url:https://example.com", "url", "Example")
        graph.add_edge("url:https://example.com", "topic:agents", "mentions", {"source": "a"})
        graph.add_edge("url:https://example.com", "topic:agents", "mentions", {"source": "b"})

        data = graph.to_dict()

        self.assertEqual(len(data["nodes"]), 2)
        self.assertEqual(len(data["edges"]), 1)
        topic = graph.nodes["topic:agents"]
        self.assertEqual(topic.metadata["count"], 1)
        self.assertEqual(topic.metadata["last_seen"], "today")
        edge = next(iter(graph.edges.values()))
        self.assertEqual(edge.metadata["source"], "b")

    def test_report_data_renders_markdown_sections(self):
        report = ReportData(
            title="链接研究报告",
            items=[
                ReportItem(
                    name="Example",
                    url="https://example.com",
                    type="文章",
                    access_status="✅ 正常",
                    one_line="A useful example.",
                    judgment="Worth reading.",
                    next_action="Read source.",
                )
            ],
            conclusions=["Keep this source."],
        )

        markdown = report.to_markdown()

        self.assertIn("## A. 研究总览", markdown)
        self.assertIn("## B. 分类型逐条整理", markdown)
        self.assertIn("## C. 研究结论", markdown)
        self.assertIn("#### 建议的后续行动", markdown)


if __name__ == "__main__":
    unittest.main()
