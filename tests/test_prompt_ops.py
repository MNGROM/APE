import unittest

from prompt_ops import (
    apply_prompt_revision_fragment,
    normalized_contract_contains,
    normalized_contract_occurrences,
    parse_prompt_sections,
    validate_prompt_candidate,
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


def plan(*, operation: str, target: str = "") -> dict:
    return {
        "revision_plan": [
            {
                "section": "workflow",
                "operation": operation,
                "text_to_modify": target,
                "positive_trigger": "When the requirement states an explicit alternative",
                "negative_boundary": "Do not infer alternatives from unrelated actions",
            }
        ]
    }


RULE = (
    "When the requirement states an explicit alternative, model decision branches. "
    "Do not infer alternatives from unrelated actions."
)


class PromptOpsTest(unittest.TestCase):
    def test_parse_requires_all_sections_in_order(self) -> None:
        self.assertEqual(list(parse_prompt_sections(PROMPT)), [
            "agent task",
            "input",
            "output",
            "workflow",
            "knowledge",
            "rule",
        ])
        with self.assertRaisesRegex(ValueError, "Missing required prompt sections"):
            parse_prompt_sections("## output\n\nReturn PlantUML code.")

    def test_replace_changes_only_declared_section_and_preserves_other_bytes(self) -> None:
        candidate, errors = apply_prompt_revision_fragment(
            PROMPT,
            plan(operation="replace_existing", target="Extract actions."),
            RULE,
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(candidate)
        before = parse_prompt_sections(PROMPT)
        after = parse_prompt_sections(candidate or "")
        self.assertEqual(after["workflow"], RULE)
        for section in before:
            if section != "workflow":
                self.assertEqual(after[section], before[section])
        ok, validation_errors = validate_prompt_candidate(
            candidate or "",
            baseline_prompt=PROMPT,
            target_section="workflow",
        )
        self.assertTrue(ok, validation_errors)

    def test_replace_preserves_numbered_line_item_prefix(self) -> None:
        numbered_prompt = PROMPT.replace("Extract actions.", "1. Extract actions.")
        candidate, errors = apply_prompt_revision_fragment(
            numbered_prompt,
            plan(operation="replace_existing", target="1. Extract actions."),
            RULE,
        )

        self.assertEqual(errors, [])
        workflow = parse_prompt_sections(candidate or "")["workflow"]
        self.assertTrue(workflow.startswith("1. "))
        self.assertIn(RULE, workflow)

    def test_append_adds_one_fragment(self) -> None:
        candidate, errors = apply_prompt_revision_fragment(
            PROMPT,
            plan(operation="append_new"),
            RULE,
        )
        self.assertEqual(errors, [])
        workflow = parse_prompt_sections(candidate or "")["workflow"]
        self.assertEqual(workflow, f"Extract actions.\n\n{RULE}")

    def test_replace_requires_one_exact_target(self) -> None:
        repeated = PROMPT.replace("Extract actions.", "Extract actions.\nExtract actions.")
        candidate, errors = apply_prompt_revision_fragment(
            repeated,
            plan(operation="replace_existing", target="Extract actions."),
            RULE,
        )
        self.assertIsNone(candidate)
        self.assertIn("found=2", errors[0])

    def test_only_current_operations_are_allowed(self) -> None:
        for operation in ("unsupported_operation_a", "unsupported_operation_b"):
            candidate, errors = apply_prompt_revision_fragment(
                PROMPT,
                plan(operation=operation, target="Extract actions."),
                RULE,
            )
            self.assertIsNone(candidate)
            self.assertIn("Invalid fragment revision operation", errors[0])

    def test_rule_must_contain_frozen_trigger_and_boundary(self) -> None:
        candidate, errors = apply_prompt_revision_fragment(
            PROMPT,
            plan(operation="append_new"),
            "Model decision branches.",
        )
        self.assertIsNone(candidate)
        self.assertIn("positive_trigger", errors[0])

    def test_contract_matching_ignores_case_punctuation_and_whitespace(self) -> None:
        text = (
            "when the requirement states an explicit alternative; "
            "do not infer alternatives from unrelated actions."
        )
        self.assertTrue(
            normalized_contract_contains(
                text,
                "When the requirement states an explicit alternative.",
            )
        )
        self.assertTrue(
            normalized_contract_contains(
                text,
                "Do not infer alternatives from unrelated actions.",
            )
        )
        self.assertEqual(
            normalized_contract_occurrences(
                text,
                "When the requirement states an explicit alternative.",
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
