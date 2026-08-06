import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from eval_seed_prompt_all import build_parser, evaluate_seed_dataset, validate_args
from utils.prompt_hash import (
    PROMPT_HASH_NORMALIZATION_VERSION,
    prompt_file_sha256,
    prompt_sha256,
)


class SeedPromptEvalConcurrencyTest(unittest.TestCase):
    def test_prompt_hash_ignores_platform_newlines_and_outer_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source.md"
            run_copy = Path(temp_dir) / "prompt_used.md"
            source.write_bytes(b"\n  first\nsecond\n")
            run_copy.write_bytes(b"first\r\nsecond")

            self.assertEqual(prompt_file_sha256(source), prompt_file_sha256(run_copy))

            bom_copy = Path(temp_dir) / "bom.md"
            bom_copy.write_bytes(b"\xef\xbb\xbffirst\nsecond")
            self.assertEqual(prompt_file_sha256(source), prompt_file_sha256(bom_copy))

    def test_prompt_hash_distinguishes_internal_content(self) -> None:
        self.assertNotEqual(prompt_sha256("first\nsecond"), prompt_sha256("first\nthird"))

    def test_prompt_hash_normalization_version_is_explicit(self) -> None:
        self.assertEqual(PROMPT_HASH_NORMALIZATION_VERSION, "utf8-sig+lf+strip-v1")

    def test_seed_manifest_records_prompt_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "eval_seed_prompt_all.refresh_run_reports"
        ):
            args = SimpleNamespace(
                case_concurrency=1,
                element_extractor="rule",
                llm_element_metrics=False,
                metric_matcher="difflib",
                max_test_cases=1,
                test_sample_strategy="prefix",
            )
            dataset_dir = Path(temp_dir) / "bp"
            with patch(
                "eval_seed_prompt_all.evaluate_cases",
                return_value=([], {"count": 0.0}),
            ):
                evaluate_seed_dataset(
                    prompt="seed prompt",
                    cases=[],
                    dataset="bp",
                    args=args,
                    llm_client=object(),
                    dataset_dir=dataset_dir,
                )
            manifest = json.loads(
                (dataset_dir / "iteration_000" / "manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["prompt_sha256"], prompt_sha256("seed prompt"))
            self.assertEqual(
                manifest["prompt_hash_normalization"],
                PROMPT_HASH_NORMALIZATION_VERSION,
            )

    def test_dataset_scheduler_defaults_to_gate2(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "run_dataset_pairs.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn('"--gate2"', script)
        self.assertIn('"--gate2-size", "30"', script)
        self.assertIn('"--gate2-seed", "20260630"', script)
        self.assertEqual(script.count('"--stop-after-first-apply"'), 1)
        self.assertIn('"rac", "us"', script)
        self.assertIn("[switch]$NoGate2", script)
        self.assertIn('"--candidate-application-mode", "diagnostic-apply"', script)
        self.assertIn('"--do-sample", "omit"', script)
        self.assertIn('APE_LLM_PROVIDER', script)
        self.assertIn('DEEPSEEK_API_KEY', script)
        self.assertIn('[int]$StatusIntervalSeconds = 10', script)
        self.assertIn('[int]$HeldoutRepeats = 1', script)
        self.assertIn('"--heldout-repeats", "$HeldoutRepeats"', script)
        self.assertIn('heldout_repeats=$HeldoutRepeats', script)
        self.assertIn('heldout_repeat={5}', script)
        self.assertIn('[scheduler][status]', script)
        self.assertIn('recent_eval', script)
        self.assertIn('Write-ActiveStatus', script)

    def test_seed_ab_scheduler_uses_provider_environment(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "run_seed_ab.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn('APE_LLM_PROVIDER', script)
        self.assertIn('DEEPSEEK_MODEL', script)
        self.assertIn('"--do-sample", "omit"', script)

    def test_case_concurrency_cli_is_positive(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--case-concurrency",
                "10",
                "--mock-with-gold",
                "--no-llm-element-metrics",
                "--element-extractor",
                "rule",
            ]
        )
        validate_args(args)
        self.assertEqual(args.case_concurrency, 10)

        args.case_concurrency = 0
        with self.assertRaisesRegex(ValueError, "--case-concurrency must be positive"):
            validate_args(args)

    def test_seed_evaluation_rejects_nonzero_temperature(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--mock-with-gold",
                "--no-llm-element-metrics",
                "--element-extractor",
                "rule",
                "--temperature",
                "0.1",
            ]
        )

        with self.assertRaisesRegex(ValueError, "All model temperatures must be 0"):
            validate_args(args)

    def test_dataset_evaluation_forwards_case_concurrency(self) -> None:
        args = SimpleNamespace(case_concurrency=10)
        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "eval_seed_prompt_all.evaluate_cases",
            return_value=([], {"count": 1.0}),
        ) as evaluate_mock, patch(
            "eval_seed_prompt_all.refresh_run_reports"
        ):
            evaluate_seed_dataset(
                prompt="prompt",
                cases=[object()],
                dataset="bp",
                args=args,
                llm_client=object(),
                dataset_dir=Path(temp_dir),
            )

        self.assertEqual(evaluate_mock.call_args.kwargs["case_concurrency"], 10)


if __name__ == "__main__":
    unittest.main()
