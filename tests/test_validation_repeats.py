import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from ape_datasets.lato import Case
from run import (
    case_split_fingerprint,
    evaluate_gate,
    iteration_paths,
    run_validation_calibration,
    write_data_split_summary,
)
from utils.io import write_text


def summary(*, node: float, relation: float = 0.5, compile_rate: float = 1.0) -> dict[str, float]:
    return {
        "count": 3.0,
        "syntax_pass_rate": compile_rate,
        "plantuml_compilation_pass_rate": compile_rate,
        "infrastructure_error_rate": 0.0,
        "llm_element_evaluated": 3.0,
        "llm_element_failed": 0.0,
        "llm_node_precision": node,
        "llm_node_recall": node,
        "llm_node_f1": node,
        "llm_relation_precision": relation,
        "llm_relation_recall": relation,
        "llm_relation_f1": relation,
    }


class ValidationRepeatTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = [
            Case(dataset="a", case_id=f"a-{index:04d}", content="R", gold_plantuml="@startuml\nstart\nstop\n@enduml")
            for index in range(1, 4)
        ]
        self.args = SimpleNamespace(
            validation_repeats=3,
            gate_concurrency=4,
            max_prompt_chars=100,
            validation_calibration_repeats=5,
            gate1=True,
            gate1_size=3,
            gate2=True,
            gate2_size=3,
            no_evolve=False,
        )

    def test_repeats_alternate_order_and_write_aggregate(self) -> None:
        calls: list[tuple[str, int, Path]] = []
        role_counts = {"baseline": 0, "candidate": 0}
        candidate_nodes = [0.72, 0.71, 0.69]

        def fake_evaluate_cases(**kwargs):
            role = "baseline" if kwargs["prompt"] == "baseline" else "candidate"
            index = role_counts[role]
            role_counts[role] += 1
            output_path = kwargs["output_path"]
            write_text(output_path, "")
            calls.append((role, kwargs["case_concurrency"], output_path))
            node = 0.7 if role == "baseline" else candidate_nodes[index]
            return [], summary(node=node)

        with tempfile.TemporaryDirectory() as temp_dir, patch("run.evaluate_cases", side_effect=fake_evaluate_cases):
            root = Path(temp_dir)
            iter_dir = root / "iteration_001"
            paths = iteration_paths(iter_dir)
            _, _, _, _, decision = evaluate_gate(
                baseline_prompt="baseline",
                candidate_prompt="candidate",
                validation_cases=self.cases,
                args=self.args,
                llm_client=object(),
                run_dir=root,
                iter_dir=iter_dir,
                paths=paths,
                iteration=1,
                phase_prefix="test",
                candidate_evidence_family="semantic",
                required_metrics=("llm_node_f1",),
            )

            self.assertEqual([role for role, _, _ in calls], ["baseline", "candidate", "candidate", "baseline", "baseline", "candidate"])
            self.assertTrue(all(concurrency == 4 for _, concurrency, _ in calls))
            self.assertTrue(decision["accepted"])
            self.assertEqual(decision["candidate_evidence_family"], "semantic")
            self.assertEqual(decision["required_metrics"], ["llm_node_f1"])
            self.assertEqual(decision["direct_metric"], "llm_node_f1")
            self.assertEqual(decision["winning_metrics"], ["llm_node_f1"])
            aggregate = json.loads(paths["validation_aggregate_summary"].read_text(encoding="utf-8"))
            self.assertEqual(len(aggregate["baseline_repeat_summaries"]), 3)
            self.assertEqual(aggregate["candidate_evidence_family"], "semantic")
            self.assertEqual(aggregate["required_metrics"], ["llm_node_f1"])
            self.assertIn("llm_node_f1", aggregate["direct_metric_results"])
            self.assertIn("llm_node_f1", aggregate["metric_results"])
            self.assertIn(
                "plantuml_compilation_pass_rate", aggregate["metric_results"]
            )
            self.assertEqual(aggregate["gate1_split_fingerprint"], case_split_fingerprint(self.cases))
            self.assertTrue((iter_dir / "gate1" / "repeat_002" / "candidate" / "summary.json").exists())

    def test_multiple_candidates_reuse_one_repeated_baseline(self) -> None:
        role_counts = {"baseline": 0, "candidate": 0}

        def fake_evaluate_cases(**kwargs):
            role = "baseline" if kwargs["prompt"] == "baseline" else "candidate"
            role_counts[role] += 1
            write_text(kwargs["output_path"], "")
            return [], summary(node=0.7 if role == "baseline" else 0.71)

        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "run.evaluate_cases", side_effect=fake_evaluate_cases
        ):
            root = Path(temp_dir)
            baseline_cache = {}
            for attempt in (1, 2):
                attempt_dir = root / f"attempt_{attempt:03d}"
                evaluate_gate(
                    baseline_prompt="baseline",
                    candidate_prompt=f"candidate_{attempt}",
                    validation_cases=self.cases,
                    args=self.args,
                    llm_client=object(),
                    run_dir=root,
                    iter_dir=attempt_dir,
                    paths=iteration_paths(attempt_dir),
                    iteration=1,
                    phase_prefix=f"test:attempt_{attempt:03d}",
                    baseline_cache=baseline_cache,
                    candidate_evidence_family="semantic",
                    required_metrics=("llm_node_f1",),
                )

            self.assertEqual(role_counts["baseline"], 3)
            self.assertEqual(role_counts["candidate"], 6)
            self.assertEqual(len(baseline_cache["repeat_summaries"]), 3)
            self.assertTrue(
                (
                    root
                    / "attempt_002"
                    / "gate1"
                    / "repeat_001"
                    / "baseline"
                    / "summary.json"
                ).exists()
            )

    def test_calibration_runs_only_configured_seed_repeats(self) -> None:
        calls: list[int] = []

        def fake_evaluate_cases(**kwargs):
            write_text(kwargs["output_path"], "")
            calls.append(kwargs["case_concurrency"])
            return [], summary(node=0.7 + 0.01 * len(calls))

        with tempfile.TemporaryDirectory() as temp_dir, patch("run.evaluate_cases", side_effect=fake_evaluate_cases):
            root = Path(temp_dir)
            result = run_validation_calibration(
                prompt="seed",
                validation_cases=self.cases,
                args=self.args,
                llm_client=object(),
                run_dir=root,
            )
            self.assertEqual(len(calls), 5)
            self.assertIn("llm_node_f1", result)
            report = json.loads((root / "validation_calibration" / "aggregate_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(report["calibration_repeats"], 5)
            self.assertEqual(report["validation_split_fingerprint"], case_split_fingerprint(self.cases))
            self.assertNotIn(
                "suggested_min_delta", report["metric_statistics"]["llm_node_f1"]
            )
            self.assertEqual(
                report["acceptance_policy"],
                "all required metric mean deltas must be positive; calibration is descriptive and never sets a threshold",
            )

    def test_gate2_evaluation_uses_fresh_baseline_each_time(self) -> None:
        role_counts = {"baseline": 0, "candidate": 0}

        def fake_evaluate_cases(**kwargs):
            role = "baseline" if kwargs["prompt"] == "baseline" else "candidate"
            role_counts[role] += 1
            write_text(kwargs["output_path"], "")
            return [], summary(node=0.7 if role == "baseline" else 0.71)

        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "run.evaluate_cases", side_effect=fake_evaluate_cases
        ):
            root = Path(temp_dir)
            for attempt in (1, 2):
                attempt_dir = root / f"attempt_{attempt:03d}"
                evaluate_gate(
                    baseline_prompt="baseline",
                    candidate_prompt=f"candidate_{attempt}",
                    validation_cases=self.cases,
                    args=self.args,
                    llm_client=object(),
                    run_dir=root,
                    iter_dir=attempt_dir,
                    paths=iteration_paths(attempt_dir),
                    iteration=1,
                    phase_prefix=f"test:attempt_{attempt:03d}",
                    baseline_cache=None,
                    candidate_evidence_family="semantic",
                    required_metrics=("llm_node_f1",),
                    gate_name="gate2",
                )

            self.assertEqual(role_counts, {"baseline": 6, "candidate": 6})
            self.assertTrue((root / "attempt_002" / "gate2" / "aggregate_summary.json").exists())

    def test_data_split_summary_records_actual_size_and_stable_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            summary_payload = write_data_split_summary(
                run_dir=root,
                args=self.args,
                train_pool_cases=self.cases,
                train_cases=self.cases[:2],
                validation_cases=self.cases[2:],
                confirmation_cases=[],
            )
            self.assertEqual(summary_payload["requested_gate1_count"], 3)
            self.assertEqual(summary_payload["actual_gate1_count"], 1)
            saved = json.loads((root / "data_split_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["gate1_split_fingerprint"], case_split_fingerprint(self.cases[2:]))


if __name__ == "__main__":
    unittest.main()
