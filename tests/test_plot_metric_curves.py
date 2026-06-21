import json
import tempfile
import unittest
from pathlib import Path

from scripts.plot_metric_curves import build_rows


def write_json(path: Path, payload: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class PlotMetricCurvesTest(unittest.TestCase):
    def test_build_rows_reads_train_gate_and_test_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            iter_dir = run_dir / "iteration_001"
            write_json(iter_dir / "evaluation" / "analysis_summary.json", {"node_f1": 0.2, "relation_f1": 0.3})
            write_json(iter_dir / "evaluation" / "gate_candidate_summary.json", {"node_f1": 0.4, "relation_f1": 0.5})
            write_json(iter_dir / "held_out_test" / "summary.json", {"node_f1": 0.6, "relation_f1": 0.7})
            write_json(run_dir / "test" / "summary.json", {"node_f1": 0.8, "relation_f1": 0.9})

            rows = build_rows(run_dir, ["node_f1", "relation_f1"])

        by_split = {row["split"]: row for row in rows}
        self.assertEqual(by_split["train_epoch"]["node_f1"], 0.2)
        self.assertEqual(by_split["gate_candidate"]["relation_f1"], 0.5)
        self.assertEqual(by_split["iteration_test"]["node_f1"], 0.6)
        self.assertEqual(by_split["final_test"]["relation_f1"], 0.9)


if __name__ == "__main__":
    unittest.main()
