import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from analysis.prompt_editor import propose_prompt_revision

TAXONOMY_PATH = Path(__file__).resolve().parents[1] / "prompt_workspace" / "mechanism_taxonomy_v1.json"

SELECTED_MECHANISM = {
    "mechanism_id": "explicit_concurrency_not_mapped",
    "mechanism_signature": {
        "failure_direction": "missing_required_parallel",
        "construct_family": "fork",
        "requirement_trigger": "explicit_concurrency",
        "gold_state": "present",
        "prediction_state": "absent",
        "node_inventory_status": "sufficient",
    },
    "supporting_evidence_ids": ["run:i001:b001:a:a-0001"],
    "positive_trigger": "Use fork for explicit concurrency.",
    "negative_boundary": "Do not use fork for ordinary lists.",
}

MISSING_LOCALIZATION = {
    "prompt_gap": "missing",
    "existing_prompt_quote": "",
    "gap_rationale": "The prompt lacks a complete explicit-concurrency boundary.",
    "section_diagnoses": [
        {
            "section": "knowledge",
            "repair_type": "construct_selection",
            "section_problem": "The fork rule lacks a negative boundary.",
            "risk_if_modified": "A broad change could trigger fork for ordinary lists.",
        }
    ],
}

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

    def chat(self, messages: list[dict[str, str]], **kwargs) -> str:
        return self.response


class PromptEditorTest(unittest.TestCase):
    def test_prompt_editor_payload_includes_edit_budget(self) -> None:
        response = json.dumps(
            {
                "revision_plan": [
                    {
                        "section": "knowledge",
                        "operation": "qualify_existing",
                        "text_to_modify": "Use fork only for explicit parallel work.",
                        "intent": "Tighten fork usage.",
                        "change_instruction": "Use fork only for explicit parallel execution.",
                    }
                ]
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompt_editor.md"
            input_path = root / "prompt_editor.input.json"
            output_path = root / "prompt_editor.output.json"
            prompt_path.write_text("Editor system prompt", encoding="utf-8")
            edit_budget = {
                "max_revision_items": 1,
                "guidance": ["Revise only the single highest-impact section."],
            }
            args = SimpleNamespace(
                no_evolve=False,
                prompt_editor_prompt_path=prompt_path,
                editor_temperature=0.1,
                editor_max_tokens=1234,
                editor_thinking="disabled",
                mechanism_taxonomy_path=TAXONOMY_PATH,
            )

            failure_analysis = {
                "error_patterns": [
                    {
                        "failure_direction": "missing_required_parallel",
                        "construct_family": "fork",
                        "requirement_trigger": "explicit_concurrency",
                        "gold_state": "present",
                        "prediction_state": "absent",
                        "node_inventory_status": "sufficient",
                        "evidence_basis": "requirement_and_gold",
                        "evidence_claims": [
                            {
                                "evidence_id": "run:i001:b001:a:a-0001",
                                "role": "primary",
                                "requirement_quote": "tasks run concurrently",
                                "error_anchor": "A -> B (fork)",
                            }
                        ],
                    }
                ]
            }

            result = propose_prompt_revision(
                current_prompt=PROMPT,
                failure_analysis=failure_analysis,
                error_localization=MISSING_LOCALIZATION,
                selected_mechanism=SELECTED_MECHANISM,
                edit_budget=edit_budget,
                args=args,
                llm_client=FakeLLMClient(response),
                output_input_path=input_path,
                output_path=output_path,
                state_dir=root,
                iteration=1,
            )

            self.assertIsNotNone(result)
            payload = json.loads(input_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["edit_budget"], edit_budget)
            self.assertEqual(result["mechanism_id"], "explicit_concurrency_not_mapped")
            self.assertEqual(result["revision_plan"][0]["positive_trigger"], SELECTED_MECHANISM["positive_trigger"])

    def test_prompt_editor_rejects_multiple_revision_items(self) -> None:
        response = json.dumps(
            {
                "revision_plan": [
                    {
                        "section": "workflow",
                        "operation": "qualify_existing",
                        "text_to_modify": "Generate the diagram directly.",
                        "intent": "Improve activity extraction.",
                        "positive_trigger": "Extract explicit actions.",
                        "negative_boundary": "Do not invent actions.",
                        "change_instruction": "Identify activities before control flow.",
                    },
                    {
                        "section": "knowledge",
                        "operation": "qualify_existing",
                        "text_to_modify": "Use fork only for explicit parallel work.",
                        "intent": "Tighten fork usage.",
                        "positive_trigger": "Use fork for explicit concurrency.",
                        "negative_boundary": "Do not use fork for lists.",
                        "change_instruction": "Use fork only for explicit parallel execution.",
                    },
                ]
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompt_editor.md"
            input_path = root / "prompt_editor.input.json"
            output_path = root / "prompt_editor.output.json"
            prompt_path.write_text("Editor system prompt", encoding="utf-8")
            args = SimpleNamespace(
                no_evolve=False,
                prompt_editor_prompt_path=prompt_path,
                editor_temperature=0.1,
                editor_max_tokens=1234,
                editor_thinking="disabled",
                mechanism_taxonomy_path=TAXONOMY_PATH,
            )

            failure_analysis = {
                "error_patterns": [
                    {
                        "failure_direction": "missing_required_parallel",
                        "construct_family": "fork",
                        "requirement_trigger": "explicit_concurrency",
                        "gold_state": "present",
                        "prediction_state": "absent",
                        "node_inventory_status": "sufficient",
                        "evidence_basis": "requirement_and_gold",
                        "evidence_claims": [
                            {
                                "evidence_id": "run:i001:b001:a:a-0001",
                                "role": "primary",
                                "requirement_quote": "tasks run concurrently",
                                "error_anchor": "A -> B (fork)",
                            }
                        ],
                    }
                ]
            }

            result = propose_prompt_revision(
                current_prompt=PROMPT,
                failure_analysis=failure_analysis,
                error_localization=MISSING_LOCALIZATION,
                selected_mechanism=SELECTED_MECHANISM,
                edit_budget={"guidance": []},
                args=args,
                llm_client=FakeLLMClient(response),
                output_input_path=input_path,
                output_path=output_path,
                state_dir=root,
                iteration=1,
            )

            self.assertIsNone(result)
            self.assertIn("exactly one", output_path.with_suffix(".rejected.txt").read_text(encoding="utf-8"))

    def test_ambiguous_gap_must_modify_the_cited_text_in_the_diagnosed_section(self) -> None:
        localization = {
            "prompt_gap": "ambiguous",
            "existing_prompt_quote": "Use fork only for explicit parallel work.",
            "gap_rationale": "The existing rule lacks an explicit negative boundary.",
            "section_diagnoses": [
                {
                    "section": "knowledge",
                    "repair_type": "construct_selection",
                    "section_problem": "The boundary is incomplete.",
                    "risk_if_modified": "An overbroad change could suppress valid concurrency.",
                }
            ],
        }
        response = json.dumps(
            {
                "revision_plan": [
                    {
                        "section": "knowledge",
                        "operation": "append_new",
                        "intent": "Add another fork rule.",
                        "change_instruction": "Repeat the explicit-concurrency rule.",
                    }
                ]
            }
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = root / "prompt_editor.md"
            input_path = root / "prompt_editor.input.json"
            output_path = root / "prompt_editor.output.json"
            prompt_path.write_text("Editor system prompt", encoding="utf-8")
            args = SimpleNamespace(
                no_evolve=False,
                prompt_editor_prompt_path=prompt_path,
                editor_temperature=0.0,
                editor_max_tokens=1234,
                editor_thinking="disabled",
            )
            result = propose_prompt_revision(
                current_prompt=PROMPT,
                failure_analysis={"error_patterns": []},
                error_localization=localization,
                selected_mechanism=SELECTED_MECHANISM,
                edit_budget={"guidance": []},
                args=args,
                llm_client=FakeLLMClient(response),
                output_input_path=input_path,
                output_path=output_path,
                state_dir=root,
                iteration=1,
            )
            rejection = output_path.with_suffix(".rejected.txt").read_text(encoding="utf-8")
            self.assertIsNone(result)
            self.assertIn("must revise existing text", rejection)


if __name__ == "__main__":
    unittest.main()
