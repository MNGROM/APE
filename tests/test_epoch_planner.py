import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from analysis.epoch_planner import plan_epoch_revision
from run import build_parser, make_edit_budget


PROMPT = """## agent task

You generate UML activity diagrams.

## input

Read requirements.

## output

Return PlantUML code.

## workflow

Generate the diagram directly.

## knowledge

Use fork only for explicit parallel work.

## rule

Keep labels concise.
"""


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict] = []

    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        self.calls.append({"messages": messages, "kwargs": kwargs})
        return self.response


class EpochPlannerTest(unittest.TestCase):
    def test_parser_defaults_to_epoch_training_mode(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(args.epoch_planner_thinking, "inherit")
        self.assertFalse(args.eval_initial_test)
        self.assertEqual(args.initial_max_sections_per_edit, 3)
        self.assertEqual(args.max_sections_per_edit, 1)

    def test_parser_enables_initial_test_baseline(self) -> None:
        args = build_parser().parse_args(["--eval-initial-test"])

        self.assertTrue(args.eval_initial_test)

    def test_plan_epoch_revision_builds_payload_and_normalizes_output(self) -> None:
        response = json.dumps(
            {
                "revision_plan": [
                    {
                        "section": "Knowledge",
                        "intent": "Constrain fork usage.",
                        "change_instruction": "Use forks only when requirements explicitly describe parallel execution.",
                    }
                ]
            }
        )
        llm_client = FakeLLMClient(response)
        batch_inputs = [
            {
                "batch_index": 1,
                "analysis_summary": {"relation_f1": 0.2},
                "revision_plan": [
                    {
                        "section": "knowledge",
                        "intent": "Avoid extra fork nodes.",
                        "change_instruction": "Tighten concurrency evidence.",
                    }
                ],
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "epoch_planner.md"
            input_path = root / "epoch_planner.input.json"
            output_path = root / "epoch_planner.output.json"
            prompt_path.write_text("Planner system prompt", encoding="utf-8")
            args = SimpleNamespace(
                epoch_planner_prompt_path=prompt_path,
                epoch_planner_temperature=0.1,
                epoch_planner_max_tokens=1234,
                epoch_planner_thinking="disabled",
                max_sections_per_edit=0,
            )
            edit_budget = {
                "max_revision_items": 1,
                "guidance": ["Merge batch-local plans into the smallest revision."],
            }

            result = plan_epoch_revision(
                current_prompt=PROMPT,
                batch_revision_inputs=batch_inputs,
                edit_budget=edit_budget,
                args=args,
                llm_client=llm_client,
                output_input_path=input_path,
                output_path=output_path,
                state_dir=root,
                iteration=3,
            )

            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result["revision_plan"][0]["section"], "knowledge")
            payload = json.loads(input_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["batch_revision_inputs"], batch_inputs)
            self.assertEqual(payload["edit_budget"], edit_budget)
            self.assertNotIn("planning_constraints", payload)
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), result)
            self.assertEqual(llm_client.calls[0]["messages"][0]["content"], "Planner system prompt")
            self.assertEqual(llm_client.calls[0]["kwargs"]["temperature"], 0.1)
            self.assertEqual(llm_client.calls[0]["kwargs"]["max_tokens"], 1234)
            self.assertEqual(llm_client.calls[0]["kwargs"]["thinking"], "disabled")
            self.assertEqual(llm_client.calls[0]["kwargs"]["retry_phase"], "epoch_planner")

    def test_make_edit_budget_switches_after_first_accepted_update(self) -> None:
        args = build_parser().parse_args([
            "--initial-max-sections-per-edit",
            "3",
            "--max-sections-per-edit",
            "1",
        ])

        editor_budget = make_edit_budget(has_accepted_update=False, args=args, agent="prompt_editor")
        planner_initial_budget = make_edit_budget(has_accepted_update=False, args=args, agent="epoch_planner")
        planner_refinement_budget = make_edit_budget(has_accepted_update=True, args=args, agent="epoch_planner")

        self.assertNotIn("max_revision_items", editor_budget)
        self.assertEqual(planner_initial_budget["max_revision_items"], 3)
        self.assertEqual(planner_refinement_budget["max_revision_items"], 1)


if __name__ == "__main__":
    unittest.main()
