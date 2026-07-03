import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from analysis.prompt_editor import propose_prompt_revision


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
                        "section": "rule",
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
            )

            result = propose_prompt_revision(
                current_prompt=PROMPT,
                failure_analysis={"error_patterns": []},
                error_localization={"section_diagnoses": []},
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

    def test_prompt_editor_does_not_hard_limit_section_count(self) -> None:
        response = json.dumps(
            {
                "revision_plan": [
                    {
                        "section": "workflow",
                        "intent": "Improve activity extraction.",
                        "change_instruction": "Identify activities before control flow.",
                    },
                    {
                        "section": "rule",
                        "intent": "Tighten fork usage.",
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
            )

            result = propose_prompt_revision(
                current_prompt=PROMPT,
                failure_analysis={"error_patterns": []},
                error_localization={"section_diagnoses": []},
                edit_budget={"guidance": []},
                args=args,
                llm_client=FakeLLMClient(response),
                output_input_path=input_path,
                output_path=output_path,
                state_dir=root,
                iteration=1,
            )

            self.assertIsNotNone(result)
            payload = json.loads(input_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["edit_budget"], {"guidance": []})
            self.assertNotIn("max_revision_items", payload["edit_budget"])


if __name__ == "__main__":
    unittest.main()
