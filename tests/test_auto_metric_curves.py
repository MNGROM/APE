import json
import tempfile
import unittest
from pathlib import Path

from run import write_metric_curves


def write_json(path: Path, payload: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class AutoMetricCurvesTest(unittest.TestCase):
    def test_write_metric_curves_creates_run_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            write_json(
                run_dir / "iteration_001" / "evaluation" / "analysis_summary.json",
                {
                    "node_f1": 0.2,
                    "relation_f1": 0.3,
                    "plantuml_compilation_pass_rate": 1.0,
                },
            )

            write_metric_curves(run_dir)

            self.assertTrue((run_dir / "metric_curves.csv").exists())
            self.assertTrue((run_dir / "metric_curves.png").exists())


if __name__ == "__main__":
    unittest.main()
