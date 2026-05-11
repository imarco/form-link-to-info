import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GPTSafeSurfaceTests(unittest.TestCase):
    def test_install_surface_avoids_sensitive_implementation_language(self):
        forbidden = [
            "绕" + "过",
            "规" + "避",
            "穿" + "透",
            "反" + "爬",
            "Cloud" + "flare",
            "document" + ".cookie",
            "local" + "Storage",
            "coo" + "kies",
            "注入 " + "coo" + "kies",
            "保存" + "凭据",
            "anti" + "-bot",
            "by" + "pass",
        ]
        roots = [
            ROOT / ".gitignore",
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "docs",
            ROOT / "evals",
            ROOT / "references",
            ROOT / "scripts",
            ROOT / "tests",
        ]
        checked_files = []
        violations = []

        for root in roots:
            paths = [root] if root.is_file() else sorted(root.rglob("*"))
            for path in paths:
                if not path.is_file():
                    continue
                if path.suffix not in {".md", ".toml", ".json", ".py", ".sh"}:
                    continue
                checked_files.append(path)
                text = path.read_text(encoding="utf-8")
                for term in forbidden:
                    if term in text:
                        violations.append(f"{path.relative_to(ROOT)} contains {term!r}")

        self.assertGreater(len(checked_files), 20)
        self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
