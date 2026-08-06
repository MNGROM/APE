import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from reporting import (
    build_validation_impact_summary,
    refresh_run_reports,
    write_iteration_reports,
    write_validation_impact_report,
)


class ReportingTest(unittest.TestCase):
    @staticmethod
    def impact_record(*, dataset: str, case_id: str, node: float, relation: float, status: str = "success"):
        return SimpleNamespace(
            dataset=dataset,
            case_id=case_id,
            syntax=SimpleNamespace(passed=True),
            plantuml_compilation=SimpleNamespace(passed=True),
            llm_element_metrics=SimpleNamespace(
                status=status,
                node_metrics=SimpleNamespace(precision=node, recall=node, f1=node),
                relation_metrics=SimpleNamespace(precision=relation, recall=relation, f1=relation),
            ),
        )

    def test_metrics_overview_uses_iteration_test_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "prompt_initial.md").write_text("seed prompt\n", encoding="utf-8")

            baseline_dir = run_dir / "iteration_000" / "test"
            baseline_dir.mkdir(parents=True)
            (baseline_dir / "summary.json").write_text(
                json.dumps({"count": 3.0, "node_f1": 0.5, "relation_f1": 0.6}),
                encoding="utf-8",
            )

            iter_dir = run_dir / "iteration_001"
            (iter_dir / "prompts").mkdir(parents=True)
            (iter_dir / "prompts" / "before.md").write_text("before\n", encoding="utf-8")
            (iter_dir / "prompts" / "after.md").write_text("after\n", encoding="utf-8")

            evaluation_dir = iter_dir / "evaluation"
            evaluation_dir.mkdir(parents=True)
            (evaluation_dir / "analysis_summary.json").write_text(
                json.dumps({"count": 3.0, "node_f1": 0.1, "relation_f1": 0.2}),
                encoding="utf-8",
            )
            (evaluation_dir / "gate_candidate_summary.json").write_text(
                json.dumps({"count": 3.0, "node_f1": 0.3, "relation_f1": 0.4}),
                encoding="utf-8",
            )

            test_dir = iter_dir / "test"
            test_dir.mkdir(parents=True)
            (test_dir / "summary.json").write_text(
                json.dumps({"count": 3.0, "node_f1": 0.7, "relation_f1": 0.8}),
                encoding="utf-8",
            )

            refresh_run_reports(run_dir)

            overview = (run_dir / "metrics_overview.md").read_text(encoding="utf-8")
            self.assertIn("iteration_000:test", overview)
            self.assertIn("iteration_001:test", overview)
            self.assertIn("0.5000", overview)
            self.assertIn("0.6000", overview)
            self.assertIn("0.7000", overview)
            self.assertIn("0.8000", overview)
            self.assertNotIn("analysis_current", overview)
            self.assertNotIn("gate_candidate", overview)

    def test_iteration_report_prefers_gate1_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            iter_dir = run_dir / "iteration_001"
            (iter_dir / "prompts").mkdir(parents=True)
            (iter_dir / "prompts" / "before.md").write_text("before\n", encoding="utf-8")
            (iter_dir / "prompts" / "after.md").write_text("after\n", encoding="utf-8")
            validation_dir = iter_dir / "gate1"
            validation_dir.mkdir(parents=True)
            (validation_dir / "baseline_summary.json").write_text(
                json.dumps({"count": 2.0, "node_f1": 0.4, "relation_f1": 0.5}),
                encoding="utf-8",
            )
            (validation_dir / "candidate_summary.json").write_text(
                json.dumps({"count": 2.0, "node_f1": 0.6, "relation_f1": 0.7}),
                encoding="utf-8",
            )
            decision_dir = iter_dir / "decision"
            decision_dir.mkdir()
            (decision_dir / "acceptance.json").write_text(
                json.dumps({"accepted": True, "acceptance_mode": "standard", "evaluation_source": "gate1"}),
                encoding="utf-8",
            )

            refresh_run_reports(run_dir)

            report = (iter_dir / "reports" / "metrics_report.md").read_text(encoding="utf-8")
            self.assertIn("gate1_baseline", report)
            self.assertIn("gate1_candidate", report)
            self.assertIn("0.6000", report)

    def test_validation_impact_reports_repeat_case_and_dataset_deltas(self) -> None:
        baseline = [self.impact_record(dataset="a", case_id="a-1", node=0.5, relation=0.8)]
        candidate = [self.impact_record(dataset="a", case_id="a-1", node=0.7, relation=0.6)]
        summary = build_validation_impact_summary([(1, baseline, candidate)])
        self.assertTrue(summary["diagnostic_only"])
        self.assertEqual(summary["repeat_count"], 1)
        self.assertAlmostEqual(summary["cases"][0]["deltas"]["llm_node_f1"], 0.2)
        self.assertAlmostEqual(summary["cases"][0]["deltas"]["llm_relation_f1"], -0.2)
        self.assertEqual(summary["datasets"][0]["semantic_valid_case_count"], 1)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            json_path = root / "impact_summary.json"
            report_path = root / "impact_report.md"
            write_validation_impact_report(
                summary=summary,
                json_path=json_path,
                report_path=report_path,
            )
            saved = json.loads(json_path.read_text(encoding="utf-8"))
            report = report_path.read_text(encoding="utf-8")
        self.assertEqual(saved["acceptance_effect"], "none")
        self.assertIn("diagnostic only", report)
        self.assertIn("a-1", report)

    def test_iteration_report_records_diagnostic_gate_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            iter_dir = Path(temp_dir) / "iteration_005"
            acceptance = {
                "accepted": False,
                "applied": False,
                "acceptance_mode": "rejected",
                "acceptance_policy": "all-required-positive-mean-delta",
                "gate_sequence_policy": "gate1-then-fresh-gate2",
                "candidate_evidence_family": "compile",
                "required_metrics": ["plantuml_compilation_pass_rate"],
                "non_improving_required_metrics": [
                    "plantuml_compilation_pass_rate"
                ],
                "direct_metric": "plantuml_compilation_pass_rate",
                "rejection_reasons": ["required_metric_not_improved"],
                "acceptance_decision": {
                    "schema_version": "two-stage-gate-v1",
                    "acceptance_policy": "all-required-positive-mean-delta",
                    "gate_sequence_policy": "gate1-then-fresh-gate2",
                    "candidate_evidence_family": "compile",
                    "required_metrics": ["plantuml_compilation_pass_rate"],
                    "required_metric_results": {
                        "plantuml_compilation_pass_rate": {"mean_delta": 0.0}
                    },
                    "non_improving_required_metrics": [
                        "plantuml_compilation_pass_rate"
                    ],
                    "direct_metric": "plantuml_compilation_pass_rate",
                    "direct_metric_results": {
                        "plantuml_compilation_pass_rate": {"mean_delta": 0.0}
                    },
                    "evaluation_valid": True,
                    "winning_metrics": ["llm_relation_f1"],
                    "metric_results": {
                        "plantuml_compilation_pass_rate": {
                            "available": True,
                            "repeat_deltas": [0.0, 0.0, 0.0],
                            "mean_delta": 0.0,
                            "positive_mean_delta": False,
                        }
                    },
                    "gate1_decision": {
                        "accepted": True,
                        "baseline_summary": {"llm_node_f1": 0.5},
                        "candidate_summary": {"llm_node_f1": 0.6},
                    },
                    "gate2_decision": {
                        "accepted": False,
                        "baseline_summary": {"llm_node_f1": 0.55},
                        "candidate_summary": {"llm_node_f1": 0.54},
                    },
                },
                "gate1_evaluated": True,
                "gate2_evaluated": True,
            }
            write_iteration_reports(
                iter_dir=iter_dir,
                iteration=5,
                prompt_before="before",
                prompt_after="before",
                candidate_prompt="candidate",
                analysis_summary={},
                baseline_gate_summary={},
                candidate_summary={},
                acceptance=acceptance,
            )

            prompt_report = (iter_dir / "reports" / "prompt_change.md").read_text(
                encoding="utf-8"
            )
            metrics_report = (iter_dir / "reports" / "metrics_report.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("candidate_evidence_family: compile", prompt_report)
            self.assertIn(
                "acceptance_policy: all-required-positive-mean-delta",
                prompt_report,
            )
            self.assertIn(
                "required_metrics: plantuml_compilation_pass_rate", prompt_report
            )
            self.assertIn(
                "non_improving_required_metrics: plantuml_compilation_pass_rate",
                prompt_report,
            )
            self.assertIn(
                '"acceptance_policy": "all-required-positive-mean-delta"',
                metrics_report,
            )
            self.assertIn(
                '"gate_sequence_policy": "gate1-then-fresh-gate2"',
                metrics_report,
            )
            self.assertIn(
                '"direct_metric": "plantuml_compilation_pass_rate"',
                metrics_report,
            )
            self.assertIn('"metric_results"', metrics_report)
            self.assertNotIn('"semantic_safety_results"', metrics_report)
            self.assertNotIn('"compile_safety_results"', metrics_report)
            self.assertIn('"gate2_decision"', metrics_report)
            self.assertIn("gate2_evaluated: True", prompt_report)

    def test_iteration_report_renders_per_dataset_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            iter_dir = Path(temp_dir) / "iteration_006"
            per_dataset = {
                "bp": {
                    "case_count": 6,
                    "repeat_count": 3,
                    "metrics": {
                        "llm_node_f1": {"mean_delta": 0.0653},
                        "llm_relation_f1": {"mean_delta": 0.0619},
                        "plantuml_compilation_pass_rate": {"mean_delta": 0.0},
                    },
                },
                "us": {
                    "case_count": 6,
                    "repeat_count": 3,
                    "metrics": {
                        "llm_node_f1": {"mean_delta": -0.0322},
                        "llm_relation_f1": {"mean_delta": -0.0863},
                        "plantuml_compilation_pass_rate": {"mean_delta": 0.0},
                    },
                },
            }
            acceptance = {
                "accepted": True,
                "applied": True,
                "acceptance_mode": "cumulative_gate",
                "rejection_reasons": [],
                "acceptance_decision": {
                    "schema_version": "two-stage-gate-v1",
                    "evaluation_valid": True,
                    "metric_results": {},
                    "per_dataset_metric_results": per_dataset,
                    "gate1_decision": {
                        "accepted": True,
                        "baseline_summary": {"llm_node_f1": 0.5},
                        "candidate_summary": {"llm_node_f1": 0.6},
                        "per_dataset_metric_results": per_dataset,
                    },
                    "gate2_decision": {
                        "accepted": True,
                        "baseline_summary": {"llm_node_f1": 0.55},
                        "candidate_summary": {"llm_node_f1": 0.60},
                        "per_dataset_metric_results": per_dataset,
                    },
                },
                "gate1_evaluated": True,
                "gate2_evaluated": True,
            }
            write_iteration_reports(
                iter_dir=iter_dir,
                iteration=6,
                prompt_before="before",
                prompt_after="after",
                candidate_prompt="candidate",
                analysis_summary={},
                baseline_gate_summary={},
                candidate_summary={},
                acceptance=acceptance,
            )

            metrics_report = (iter_dir / "reports" / "metrics_report.md").read_text(
                encoding="utf-8"
            )

        self.assertIn("Per-dataset deltas (diagnostic)", metrics_report)
        # The opposing per-dataset effects must both be visible.
        self.assertIn("0.0653", metrics_report)
        self.assertIn("-0.0322", metrics_report)
        self.assertIn("| gate1 | bp |", metrics_report)
        self.assertIn("| gate2 | us |", metrics_report)

    def test_metrics_overview_reports_heldout_repeat_deltas(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            for iteration, node_values in {
                0: [0.80, 0.82],
                1: [0.83, 0.81],
            }.items():
                test_dir = run_dir / f"iteration_{iteration:03d}" / "test"
                test_dir.mkdir(parents=True)
                summaries = [
                    {
                        "llm_node_f1": node,
                        "llm_relation_f1": 0.60 + index * 0.01,
                        "plantuml_compilation_pass_rate": 1.0,
                    }
                    for index, node in enumerate(node_values)
                ]
                (test_dir / "summary.json").write_text(
                    json.dumps(
                        {
                            "llm_node_f1": sum(node_values) / len(node_values),
                            "llm_relation_f1": 0.605,
                            "plantuml_compilation_pass_rate": 1.0,
                        }
                    ),
                    encoding="utf-8",
                )
                (test_dir / "repeats.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "heldout-repeats-v1",
                            "diagnostic_only": True,
                            "repeat_count": 2,
                            "repeat_summaries": summaries,
                        }
                    ),
                    encoding="utf-8",
                )

            refresh_run_reports(run_dir)
            metrics_overview = (run_dir / "metrics_overview.md").read_text(
                encoding="utf-8"
            )

            self.assertIn("## Heldout Repeats", metrics_overview)
            self.assertIn("## Heldout Repeat Deltas", metrics_overview)
            self.assertIn("iteration_001 | llm_node_f1", metrics_overview)
            self.assertIn("0.0300, -0.0100", metrics_overview)
            self.assertIn("diagnostic-only", metrics_overview)


if __name__ == "__main__":
    unittest.main()
