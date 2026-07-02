import unittest

from prompt_ops import normalize_prompt_revision_plan, validate_prompt_revision_plan


class PromptOpsTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
