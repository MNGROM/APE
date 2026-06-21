import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run
from ape_datasets.lato import Case


class IterationHeldOutTest(unittest.TestCase):
    def test_iteration_held_out_artifact_is_diagnostic_only(self) -> None:
        case = Case(dataset="demo", case_id="case-1", content="Do work", gold_plantuml="@startuml\n@enduml")
        summary = {
            "count": 1.0,
            "plantuml_compilation_pass_rate": 1.0,
            "node_f1": 0.5,
            "relation_f1": 0.25,
        }
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            iter_dir = run_dir / "iteration_001"
            prompt_path = iter_dir / "prompts" / "after.md"
            manifest = {"stages": {}}

            with patch.object(run, "evaluate_cases", return_value=([], summary)) as evaluate_cases:
                result = run.evaluate_iteration_held_out_test(
                    args=argparse.Namespace(),
                    llm_client=object(),
                    test_cases=[case],
                    test_dataset="demo",
                    run_dir=run_dir,
                    iter_dir=iter_dir,
                    iteration=1,
                    prompt="accepted prompt",
                    prompt_path=prompt_path,
                    manifest=manifest,
                )

            self.assertEqual(result, summary)
            evaluate_cases.assert_called_once()
            held_out_manifest = json.loads((iter_dir / "held_out_test" / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(held_out_manifest["diagnostic_only"])
            self.assertFalse(held_out_manifest["used_by_agents"])
            self.assertFalse(held_out_manifest["used_by_acceptance_gate"])
            self.assertTrue((iter_dir / "held_out_test" / "summary.json").exists())


if __name__ == "__main__":
    unittest.main()
