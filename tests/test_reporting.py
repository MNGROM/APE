import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from reporting import (
    build_validation_impact_summary,
    refresh_run_reports,
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

    def test_iteration_report_prefers_validation_gate_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            iter_dir = run_dir / "iteration_001"
            (iter_dir / "prompts").mkdir(parents=True)
            (iter_dir / "prompts" / "before.md").write_text("before\n", encoding="utf-8")
            (iter_dir / "prompts" / "after.md").write_text("after\n", encoding="utf-8")
            validation_dir = iter_dir / "validation_gate"
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
                json.dumps({"accepted": True, "acceptance_mode": "standard", "evaluation_source": "validation_gate"}),
                encoding="utf-8",
            )

            refresh_run_reports(run_dir)

            report = (iter_dir / "reports" / "metrics_report.md").read_text(encoding="utf-8")
            self.assertIn("validation_baseline", report)
            self.assertIn("validation_candidate", report)
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


if __name__ == "__main__":
    unittest.main()
