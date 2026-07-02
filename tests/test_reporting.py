import json
import tempfile
import unittest
from pathlib import Path

from reporting import refresh_run_reports


class ReportingTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
