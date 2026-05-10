import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from linky.extract import extract_url
from linky.strategy import load_strategy, resolve_provider_chain, trace_enabled


class StrategyAndExtractionTests(unittest.TestCase):
    def setUp(self):
        self.strategy = load_strategy(ROOT / "references" / "fetch-strategy.toml")

    def test_loads_fallback_chain_from_toml(self):
        chain = resolve_provider_chain("https://example.com/post", self.strategy)

        self.assertEqual(chain[:3], ["jina", "trafilatura", "scrapling"])
        self.assertTrue(trace_enabled(self.strategy))

    def test_domain_route_override_skips_layers(self):
        chain = resolve_provider_chain("https://mp.weixin.qq.com/s/example", self.strategy)

        self.assertEqual(chain[0], "scrapling")
        self.assertNotIn("jina", chain)

    def test_quality_driven_fallback_records_trace(self):
        def bad_provider(url, provider, strategy):
            return {"markdown": "login", "metadata": {"name": "bad"}}

        def good_provider(url, provider, strategy):
            return {
                "markdown": "# Good Article\n\n"
                "This useful article has enough text and source metadata.\n\n"
                "It contains several paragraphs for scoring.\n\n"
                "Published by Example with a [source](https://example.com).",
                "metadata": {"name": "good"},
            }

        strategy = {
            "global": {"quality_threshold": 0.55},
            "fallback_chain": [{"id": "bad"}, {"id": "good"}],
            "quality": {"min_score": 0.55},
        }

        result = extract_url(
            "https://example.com",
            strategy=strategy,
            providers={"bad": bad_provider, "good": good_provider},
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.provider, "good")
        self.assertEqual(result.trace.attempts[0].fallback_reason, "low_quality")
        self.assertEqual(result.trace.final_provider, "good")

    def test_legacy_scrapling_cli_help_is_compatible(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "scrapling_fetch.py"), "--help"],
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0)
        self.assertIn("scrapling_fetch.py", proc.stdout)

    def test_legacy_scrapling_function_is_import_compatible(self):
        import scripts.scrapling_fetch as scrapling_fetch

        self.assertTrue(callable(scrapling_fetch.fetch_and_extract))

    def test_browser_command_provider_executes_configured_command(self):
        strategy = {
            "global": {"quality_threshold": 0.55, "timeout_seconds": 5, "max_chars": 30000},
            "fallback_chain": [
                {
                    "id": "browser",
                    "command": (
                        "python3 -c \"print('# Browser Page\\n\\n"
                        "This browser fallback page has source metadata.\\n\\n"
                        "It includes enough paragraphs for quality scoring.\\n\\n"
                        "Published by Linky with a [source](https://example.com).')\""
                    ),
                }
            ],
            "quality": {"min_score": 0.55},
        }

        result = extract_url("https://example.com/browser-only", strategy=strategy)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.provider, "browser")
        self.assertEqual(result.trace.final_provider, "browser")


if __name__ == "__main__":
    unittest.main()
