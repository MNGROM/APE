import json
import tempfile
import unittest
from pathlib import Path

from reporting import refresh_run_reports


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, float]) -> None:
    write_text(path, json.dumps(payload))


class ReportingHeldOutTest(unittest.TestCase):
    def test_metrics_overview_includes_iteration_held_out_test(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            iter_dir = run_dir / "iteration_001"
            write_text(run_dir / "prompt_initial.md", "seed")
            write_text(iter_dir / "prompts" / "before.md", "before")
            write_text(iter_dir / "prompts" / "after.md", "after")
            write_json(iter_dir / "evaluation" / "analysis_summary.json", {"count": 1.0, "node_f1": 0.1})
            write_json(iter_dir / "held_out_test" / "summary.json", {"count": 1.0, "node_f1": 0.8})

            refresh_run_reports(run_dir)

            overview = (run_dir / "metrics_overview.md").read_text(encoding="utf-8")
        self.assertIn("iteration_001:held_out_test", overview)
        self.assertIn("0.8000", overview)


if __name__ == "__main__":
    unittest.main()
