import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from analysis.error_localization import localize_errors
from prompt_ops import (
    apply_prompt_revision_fragment,
    normalize_prompt_revision_plan,
    parse_prompt_sections,
    validate_error_localization_payload,
    validate_prompt_candidate,
    validate_prompt_revision_plan,
    validate_revision_against_prompt_gap,
)


PROMPT = """## agent task

Generate UML.

## input

Read requirements.

## output

Return PlantUML code.

## workflow

Extract actions.

## knowledge

Use fork only for explicit parallel work.

## rule

Do not invent behavior.
"""


class FakeLLMClient:
    def __init__(self, response: dict) -> None:
        self.response = json.dumps(response)

    def chat(self, messages, **kwargs):
        return self.response


class PromptOpsTest(unittest.TestCase):
    def diagnosis(self, *, section: str = "workflow") -> dict:
        return {
            "section": section,
            "repair_type": "activity_extraction",
            "section_problem": "The extraction boundary is incomplete.",
            "risk_if_modified": "An overbroad rule could remove explicit actions.",
        }

    def test_revision_plan_defaults_missing_operation_to_append_new(self) -> None:
        payload = {
            "revision_plan": [
                {
                    "section": "knowledge",
                    "intent": "Add fork guidance.",
                    "change_instruction": "Add guidance for explicit parallel work.",
                }
            ]
        }

        normalized = normalize_prompt_revision_plan(payload)
        ok, errors = validate_prompt_revision_plan(normalized, max_sections=1)

        self.assertTrue(ok, errors)
        self.assertEqual(normalized["revision_plan"][0]["operation"], "append_new")

    def test_revision_plan_accepts_non_append_operation_with_text_to_modify(self) -> None:
        payload = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "qualify_existing",
                    "text_to_modify": "Use fork only for explicit parallel work.",
                    "intent": "Tighten fork usage.",
                    "change_instruction": "Exclude ordinary lists and sequential UI steps.",
                }
            ]
        }

        normalized = normalize_prompt_revision_plan(payload)
        ok, errors = validate_prompt_revision_plan(normalized, max_sections=1)

        self.assertTrue(ok, errors)
        self.assertEqual(normalized["revision_plan"][0]["operation"], "qualify_existing")
        self.assertEqual(normalized["revision_plan"][0]["text_to_modify"], "Use fork only for explicit parallel work.")

    def test_revision_plan_rejects_invalid_operation(self) -> None:
        payload = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "rewrite_everything",
                    "intent": "Change too much.",
                    "change_instruction": "Rewrite the prompt.",
                }
            ]
        }

        normalized = normalize_prompt_revision_plan(payload)
        ok, errors = validate_prompt_revision_plan(normalized, max_sections=1)

        self.assertFalse(ok)
        self.assertIn("invalid operation", "\n".join(errors))

    def test_revision_plan_requires_text_to_modify_for_existing_text_operations(self) -> None:
        payload = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "replace_existing",
                    "intent": "Replace weak guidance.",
                    "change_instruction": "Replace the existing guidance with a stricter one.",
                }
            ]
        }

        normalized = normalize_prompt_revision_plan(payload)
        ok, errors = validate_prompt_revision_plan(normalized, max_sections=1)

        self.assertFalse(ok)
        self.assertIn("text_to_modify", "\n".join(errors))

    def test_revision_plan_requires_boundaries_and_exact_existing_text(self) -> None:
        payload = {
            "revision_plan": [
                {
                    "section": "knowledge",
                    "operation": "qualify_existing",
                    "text_to_modify": "Text that is not in the section.",
                    "intent": "Constrain forks.",
                    "change_instruction": "Tighten the fork rule.",
                    "positive_trigger": "Use fork for explicit concurrency.",
                    "negative_boundary": "Do not use fork for lists.",
                }
            ]
        }
        ok, errors = validate_prompt_revision_plan(
            payload,
            max_sections=1,
            current_prompt=PROMPT,
            require_boundaries=True,
        )
        self.assertFalse(ok)
        self.assertIn("was not found", "\n".join(errors))

        payload["revision_plan"][0]["text_to_modify"] = "Use fork only for explicit parallel work."
        payload["revision_plan"][0]["negative_boundary"] = ""
        ok, errors = validate_prompt_revision_plan(
            payload,
            max_sections=1,
            current_prompt=PROMPT,
            require_boundaries=True,
        )
        self.assertFalse(ok)
        self.assertIn("negative_boundary", "\n".join(errors))

    def test_candidate_may_change_only_declared_section(self) -> None:
        candidate = PROMPT.replace(
            "Use fork only for explicit parallel work.",
            "Use fork only for explicitly concurrent execution.",
        )
        ok, errors = validate_prompt_candidate(
            candidate,
            baseline_prompt=PROMPT,
            target_section="knowledge",
        )
        self.assertTrue(ok, errors)

        candidate = candidate.replace("Do not invent behavior.", "Never invent behavior.")
        ok, errors = validate_prompt_candidate(
            candidate,
            baseline_prompt=PROMPT,
            target_section="knowledge",
        )
        self.assertFalse(ok)
        self.assertIn("change exactly", "\n".join(errors))

    def test_fragment_rewriter_replaces_one_unique_target_span(self) -> None:
        positive = "Use fork for explicit concurrency."
        negative = "Do not use fork for ordinary lists."
        plan = {
            "revision_plan": [
                {
                    "section": "knowledge",
                    "operation": "qualify_existing",
                    "text_to_modify": "Use fork only for explicit parallel work.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }
        candidate, errors = apply_prompt_revision_fragment(
            PROMPT,
            plan,
            f"{positive}\n{negative}",
        )
        self.assertIsNotNone(candidate, errors)
        assert candidate is not None
        before = parse_prompt_sections(PROMPT)
        after = parse_prompt_sections(candidate)
        self.assertEqual(
            [section for section in before if before[section] != after[section]],
            ["knowledge"],
        )

    def test_fragment_rewriter_rejects_non_unique_or_non_contiguous_target(self) -> None:
        duplicated = PROMPT.replace(
            "Use fork only for explicit parallel work.",
            "Use fork only for explicit parallel work.\nUse fork only for explicit parallel work.",
        )
        positive = "Use fork for explicit concurrency."
        negative = "Do not use fork for ordinary lists."
        plan = {
            "revision_plan": [
                {
                    "section": "knowledge",
                    "operation": "merge_existing",
                    "text_to_modify": "Use fork only for explicit parallel work.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }
        candidate, errors = apply_prompt_revision_fragment(
            duplicated,
            plan,
            f"{positive}\n{negative}",
        )
        self.assertIsNone(candidate)
        self.assertIn("exactly once", "\n".join(errors))

    def test_already_covered_requires_exact_quote_and_empty_diagnoses(self) -> None:
        payload = {
            "prompt_gap": "already_covered",
            "existing_prompt_quote": "Do not invent behavior.",
            "gap_rationale": "The rule already states the selected boundary.",
            "section_diagnoses": [],
        }
        ok, errors = validate_error_localization_payload(
            payload,
            max_sections=1,
            current_prompt=PROMPT,
        )
        self.assertTrue(ok, errors)

        payload["existing_prompt_quote"] = "Fabricated prompt text."
        ok, errors = validate_error_localization_payload(
            payload,
            max_sections=1,
            current_prompt=PROMPT,
        )
        self.assertFalse(ok)
        self.assertIn("was not found", "\n".join(errors))

    def test_ambiguous_quote_must_exist_in_the_diagnosed_section(self) -> None:
        payload = {
            "prompt_gap": "ambiguous",
            "existing_prompt_quote": "Do not invent behavior.",
            "gap_rationale": "The wording permits conflicting interpretations.",
            "section_diagnoses": [self.diagnosis(section="workflow")],
        }
        ok, errors = validate_error_localization_payload(
            payload,
            max_sections=1,
            current_prompt=PROMPT,
        )
        self.assertFalse(ok)
        self.assertIn("diagnosed section", "\n".join(errors))

    def test_missing_rejects_existing_quote_and_incomplete_diagnosis(self) -> None:
        payload = {
            "prompt_gap": "missing",
            "existing_prompt_quote": "Extract actions.",
            "gap_rationale": "A boundary is absent.",
            "section_diagnoses": [self.diagnosis()],
        }
        ok, errors = validate_error_localization_payload(
            payload,
            max_sections=1,
            current_prompt=PROMPT,
        )
        self.assertFalse(ok)
        self.assertIn("empty existing_prompt_quote", "\n".join(errors))

        payload["existing_prompt_quote"] = ""
        del payload["section_diagnoses"][0]["risk_if_modified"]
        ok, errors = validate_error_localization_payload(
            payload,
            max_sections=1,
            current_prompt=PROMPT,
        )
        self.assertFalse(ok)
        self.assertIn("risk_if_modified", "\n".join(errors))

    def test_localization_input_contains_python_selected_mechanism(self) -> None:
        response = {
            "prompt_gap": "already_covered",
            "existing_prompt_quote": "Do not invent behavior.",
            "gap_rationale": "The selected boundary is already explicit.",
            "section_diagnoses": [],
        }
        selected = {
            "mechanism_id": "unsupported_fork",
            "mechanism_signature": {"construct_family": "fork"},
            "supporting_evidence_ids": ["e1"],
            "positive_trigger": "Avoid unsupported fork.",
            "negative_boundary": "Preserve explicit concurrency.",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            system_prompt = root / "localize.md"
            input_path = root / "input.json"
            output_path = root / "output.json"
            system_prompt.write_text("Localize", encoding="utf-8")
            args = SimpleNamespace(
                error_localization_prompt_path=system_prompt,
                localization_temperature=0.0,
                localization_max_tokens=1000,
                localization_thinking="disabled",
                max_sections_per_edit=1,
            )
            result = localize_errors(
                current_prompt=PROMPT,
                failure_analysis={"error_patterns": [], "evidence_catalog": []},
                selected_mechanism=selected,
                args=args,
                llm_client=FakeLLMClient(response),
                output_input_path=input_path,
                output_path=output_path,
                state_dir=root,
                iteration=1,
            )
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        self.assertEqual(result["prompt_gap"], "already_covered")
        self.assertEqual(payload["selected_mechanism"]["mechanism_id"], "unsupported_fork")

    def test_ambiguous_revision_cannot_change_section_or_omit_the_quote(self) -> None:
        localization = {
            "prompt_gap": "ambiguous",
            "existing_prompt_quote": "Extract actions.",
            "gap_rationale": "The extraction boundary is ambiguous.",
            "section_diagnoses": [self.diagnosis(section="workflow")],
        }
        payload = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "qualify_existing",
                    "text_to_modify": "Do not invent behavior.",
                    "intent": "Change the wrong section.",
                    "change_instruction": "Add an unrelated qualification.",
                }
            ]
        }
        ok, errors = validate_revision_against_prompt_gap(payload, localization)
        self.assertFalse(ok)
        self.assertIn("must match", "\n".join(errors))
        self.assertIn("must contain", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
