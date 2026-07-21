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
                        "operation": "qualify_existing",
                        "text_to_modify": "Use fork only for explicit parallel work.",
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
        selected_mechanism = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "mechanism_signature": {
                "failure_direction": "missing_required_parallel",
                "construct_family": "fork",
                "requirement_trigger": "explicit_concurrency",
                "gold_state": "present",
                "prediction_state": "absent",
                "node_inventory_status": "sufficient",
            },
            "supporting_evidence_ids": ["e1", "e2", "e3"],
            "supporting_batch_count": 2,
            "positive_trigger": "Use fork for explicit concurrency.",
            "negative_boundary": "Do not use fork for ordinary lists.",
        }

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
                selected_mechanism=selected_mechanism,
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
            self.assertEqual(result["supporting_evidence_ids"], ["e1", "e2", "e3"])
            payload = json.loads(input_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["batch_revision_inputs"], batch_inputs)
            self.assertEqual(payload["selected_mechanism"]["mechanism_id"], "explicit_concurrency_not_mapped")
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
        self.assertEqual(planner_initial_budget["max_revision_items"], 1)
        self.assertEqual(planner_refinement_budget["max_revision_items"], 1)

    def test_epoch_planner_cannot_change_the_majority_section(self) -> None:
        response = json.dumps(
            {
                "revision_plan": [
                    {
                        "section": "workflow",
                        "operation": "qualify_existing",
                        "text_to_modify": "Generate the diagram directly.",
                        "intent": "Change another section.",
                        "change_instruction": "Revise workflow instead.",
                    }
                ]
            }
        )
        batch_inputs = [
            {
                "batch_id": 1,
                "revision_plan": [
                    {
                        "section": "knowledge",
                        "intent": "Tighten fork usage.",
                        "change_instruction": "Constrain explicit concurrency.",
                    }
                ],
            }
        ]
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "mechanism_signature": {},
            "supporting_evidence_ids": ["e1"],
            "positive_trigger": "Use fork for concurrency.",
            "negative_boundary": "Do not use fork for lists.",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "planner.md"
            output_path = root / "output.json"
            prompt_path.write_text("Planner", encoding="utf-8")
            args = SimpleNamespace(
                epoch_planner_prompt_path=prompt_path,
                epoch_planner_temperature=0.0,
                epoch_planner_max_tokens=1000,
                epoch_planner_thinking="disabled",
            )
            result = plan_epoch_revision(
                current_prompt=PROMPT,
                batch_revision_inputs=batch_inputs,
                selected_mechanism=selected,
                edit_budget={"max_revision_items": 1},
                args=args,
                llm_client=FakeLLMClient(response),
                output_input_path=root / "input.json",
                output_path=output_path,
                state_dir=root,
                iteration=1,
            )
            rejection = output_path.with_suffix(".rejected.txt").read_text(encoding="utf-8")
        self.assertIsNone(result)
        self.assertIn("strict-majority section", rejection)

    def test_epoch_planner_rejects_mixed_atomic_revision_scopes(self) -> None:
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "mechanism_signature": {
                "failure_direction": "missing_required_parallel",
                "construct_family": "fork",
                "requirement_trigger": "explicit_concurrency",
                "gold_state": "present",
                "prediction_state": "absent",
                "node_inventory_status": "sufficient",
            },
            "supporting_attribution_ids": ["attr-1"],
        }
        scope = {
            "mechanism_id": selected["mechanism_id"],
            "mechanism_signature": selected["mechanism_signature"],
            "supporting_attribution_ids": ["attr-1"],
            "prompt_gap": "missing",
            "section": "knowledge",
            "repair_type": "construct_selection",
            "existing_prompt_quote": "",
        }
        other_scope = {**scope, "repair_type": "relation_grounding"}
        batch_inputs = [
            {"batch_id": 1, "revision_plan": [{"section": "knowledge", "revision_scope": scope}]},
            {"batch_id": 2, "revision_plan": [{"section": "knowledge", "revision_scope": other_scope}]},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_path = root / "output.json"
            result = plan_epoch_revision(
                current_prompt=PROMPT,
                batch_revision_inputs=batch_inputs,
                selected_mechanism=selected,
                edit_budget={"max_revision_items": 1},
                args=SimpleNamespace(
                    epoch_planner_prompt_path=root / "planner.md",
                    epoch_planner_temperature=0.0,
                    epoch_planner_max_tokens=1000,
                    epoch_planner_thinking="disabled",
                ),
                llm_client=FakeLLMClient("{}"),
                output_input_path=root / "input.json",
                output_path=output_path,
                state_dir=root,
                iteration=1,
            )
            rejection = output_path.with_suffix(".rejected.txt").read_text(encoding="utf-8")
        self.assertIsNone(result)
        self.assertIn("one identical atomic revision scope", rejection)


if __name__ == "__main__":
    unittest.main()
