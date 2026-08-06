import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from utils.prompt_hash import prompt_file_sha256


ANALYZER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "analyze_seed_ab.py"
SPEC = importlib.util.spec_from_file_location("tracked_seed_ab_analyzer", ANALYZER_PATH)
assert SPEC is not None and SPEC.loader is not None
ANALYZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYZER)


class TrackedSeedAbAnalyzerTest(unittest.TestCase):
    def test_prompt_hash_validation_accepts_platform_newline_difference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            expected = root / "expected.md"
            run_dir = root / "run"
            run_dir.mkdir()
            expected.write_text("first\nsecond\n", encoding="utf-8")
            (run_dir / "prompt_used.md").write_bytes(b"first\r\nsecond")
            (run_dir / "run_args.json").write_text(
                json.dumps({"case_concurrency": 10, "temperature": 0, "do_sample": False}),
                encoding="utf-8",
            )
            (run_dir / "manifest.json").write_text(
                json.dumps({"prompt_sha256": prompt_file_sha256(expected)}),
                encoding="utf-8",
            )

            ANALYZER.validate_prompt_hash(
                run_dir,
                expected,
                condition="baseline",
                repeat=1,
            )

    def test_prompt_hash_validation_reports_expected_and_actual(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            expected = root / "expected.md"
            run_dir = root / "run"
            run_dir.mkdir()
            expected.write_text("expected", encoding="utf-8")
            (run_dir / "prompt_used.md").write_text("actual", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "expected=.*actual="):
                ANALYZER.validate_prompt_hash(
                    run_dir,
                    expected,
                    condition="candidate-a",
                    repeat=2,
                )

    def test_run_args_accept_deepseek_without_do_sample(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "run_args.json").write_text(
                json.dumps(
                    {
                        "case_concurrency": 10,
                        "temperature": 0,
                        "llm_provider": "deepseek",
                        "do_sample": None,
                    }
                ),
                encoding="utf-8",
            )

            ANALYZER.validate_run_args(run_dir, case_concurrency=10)

    def test_run_args_reject_deepseek_sampling_field(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "run_args.json").write_text(
                json.dumps(
                    {
                        "case_concurrency": 10,
                        "temperature": 0,
                        "llm_provider": "deepseek",
                        "do_sample": False,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "must omit do_sample"):
                ANALYZER.validate_run_args(run_dir, case_concurrency=10)

    def test_run_args_reject_provider_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "run_args.json").write_text(
                json.dumps(
                    {
                        "case_concurrency": 10,
                        "temperature": 0,
                        "llm_provider": "deepseek",
                        "do_sample": None,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Provider mismatch"):
                ANALYZER.validate_run_args(
                    run_dir,
                    case_concurrency=10,
                    expected_provider="zhipu",
                )


if __name__ == "__main__":
    unittest.main()
