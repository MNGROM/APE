import json
import tempfile
import unittest
from pathlib import Path

from reporting import refresh_run_reports
from scripts.plot_metric_curves import build_rows


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    write_text(path, json.dumps(payload))


class BatchGateReportingTest(unittest.TestCase):
    def test_batch_gate_metrics_and_acceptance_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            iter_dir = run_dir / "iteration_001"
            batch_dir = iter_dir / "train_batches" / "batch_001"
            write_text(run_dir / "prompt_initial.md", "seed")
            write_text(iter_dir / "prompts" / "before.md", "before")
            write_text(iter_dir / "prompts" / "candidate.md", "candidate")
            write_text(iter_dir / "prompts" / "after.md", "after")
            write_json(iter_dir / "evaluation" / "analysis_summary.json", {"count": 1.0, "node_f1": 0.2})
            write_json(batch_dir / "evaluation" / "analysis_summary.json", {"count": 1.0, "node_f1": 0.3})
            write_json(batch_dir / "gate" / "baseline_summary.json", {"count": 1.0, "node_f1": 0.4})
            write_json(batch_dir / "gate" / "candidate_summary.json", {"count": 1.0, "node_f1": 0.5})
            write_json(batch_dir / "decision" / "acceptance.json", {"accepted": True, "acceptance_mode": "standard", "rejection_reasons": []})

            refresh_run_reports(run_dir)
            rows = build_rows(run_dir, ["node_f1"])

            overview = (run_dir / "metrics_overview.md").read_text(encoding="utf-8")
            evolution = (run_dir / "prompt_evolution.md").read_text(encoding="utf-8")

        self.assertIn("iteration_001:batch_001:gate_candidate", overview)
        self.assertIn("batch_acceptance: 1/1 accepted", evolution)
        self.assertEqual({row["split"]: row["node_f1"] for row in rows}["gate_candidate"], 0.5)


if __name__ == "__main__":
    unittest.main()
