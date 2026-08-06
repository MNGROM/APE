import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ape_datasets.lato import Case
from run import build_parser, evaluate_iteration_test


def make_case(case_id: str) -> Case:
    return Case(
        dataset="heldout",
        case_id=case_id,
        content=f"Requirement {case_id}",
        gold_plantuml="start\nstop",
    )


class HeldoutRepeatsTest(unittest.TestCase):
    def test_repeats_keep_each_measurement_and_aggregate_top_level_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            iter_dir = root / "iteration_001"
            cases = [make_case("case-1"), make_case("case-2")]
            args = build_parser().parse_args(["--heldout-repeats", "3"])
            summaries = [
                {
                    "count": 2.0,
                    "syntax_pass_rate": 1.0,
                    "llm_element_evaluated": 2.0,
                    "llm_node_f1": 0.80,
                    "llm_relation_f1": 0.60,
                    "plantuml_compilation_pass_rate": 1.0,
                    "infrastructure_error_rate": 0.0,
                },
                {
                    "count": 2.0,
                    "syntax_pass_rate": 1.0,
                    "llm_element_evaluated": 2.0,
                    "llm_node_f1": 0.82,
                    "llm_relation_f1": 0.62,
                    "plantuml_compilation_pass_rate": 1.0,
                    "infrastructure_error_rate": 0.0,
                },
                {
                    "count": 2.0,
                    "syntax_pass_rate": 1.0,
                    "llm_element_evaluated": 2.0,
                    "llm_node_f1": 0.84,
                    "llm_relation_f1": 0.64,
                    "plantuml_compilation_pass_rate": 1.0,
                    "infrastructure_error_rate": 0.0,
                },
            ]

            with patch(
                "run.evaluate_cases", side_effect=[([], summary) for summary in summaries]
            ) as mocked:
                aggregate = evaluate_iteration_test(
                    prompt="seed",
                    test_cases=cases,
                    test_dataset="heldout",
                    args=args,
                    llm_client=object(),
                    run_dir=root,
                    iter_dir=iter_dir,
                    iteration=1,
                )

            self.assertEqual(mocked.call_count, 3)
            self.assertAlmostEqual(aggregate["llm_node_f1"], 0.82)
            repeats = json.loads(
                (iter_dir / "test" / "repeats.json").read_text(encoding="utf-8")
            )
            self.assertTrue(repeats["diagnostic_only"])
            self.assertEqual(repeats["repeat_count"], 3)
            self.assertEqual(len(repeats["repeat_summaries"]), 3)
            self.assertEqual(
                json.loads(
                    (iter_dir / "test" / "summary.json").read_text(encoding="utf-8")
                ),
                repeats["aggregate_summary"],
            )
            self.assertTrue(
                (iter_dir / "test" / "repeat_001" / "summary.json").exists()
            )
            self.assertTrue((iter_dir / "test" / "records.jsonl").exists())
            manifest = json.loads(
                (iter_dir / "test" / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["status"], "success")
            self.assertEqual(manifest["repeat_count"], 3)
            phases = [call.kwargs["phase"] for call in mocked.call_args_list]
            self.assertEqual(
                phases,
                [
                    "iteration_001:held_out_test_repeat_001_of_003",
                    "iteration_001:held_out_test_repeat_002_of_003",
                    "iteration_001:held_out_test_repeat_003_of_003",
                ],
            )


if __name__ == "__main__":
    unittest.main()
