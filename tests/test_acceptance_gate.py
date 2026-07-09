import unittest

from run import acceptance_decision


def decision(
    baseline_summary: dict[str, float],
    candidate_summary: dict[str, float],
    *,
    allow_bootstrap: bool = False,
    candidate_prompt: str = "candidate",
    baseline_prompt: str = "baseline",
    max_prompt_chars: int = 9000,
) -> dict:
    accepted, payload = acceptance_decision(
        iteration=2,
        allow_bootstrap=allow_bootstrap,
        baseline_summary=baseline_summary,
        candidate_summary=candidate_summary,
        candidate_prompt=candidate_prompt,
        baseline_prompt=baseline_prompt,
        max_prompt_chars=max_prompt_chars,
        min_relation_delta=-0.01,
        min_node_delta=-0.01,
        min_compile_delta=-0.01,
        relation_accept_delta=0.02,
        node_accept_delta=0.02,
        compile_accept_delta=0.05,
    )
    payload["accepted"] = accepted
    return payload


class AcceptanceGateTest(unittest.TestCase):
    def test_acceptance_uses_llm_judge_node_relation_benefits(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "llm_element_evaluated": 10.0,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
            },
            {
                "node_f1": 0.50,
                "relation_f1": 0.44,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.74,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "llm_element_evaluated": 10.0,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
            },
        )

        self.assertTrue(payload["accepted"])
        self.assertTrue(payload["benefit_gate"]["relation_improved"])

    def test_embedding_metrics_do_not_create_acceptance_benefit(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            {
                "node_f1": 0.56,
                "relation_f1": 0.46,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
        )

        self.assertFalse(payload["accepted"])
        self.assertFalse(payload["benefit_gate"]["relation_improved"])
        self.assertFalse(payload["benefit_gate"]["node_improved"])

    def test_llm_metrics_block_large_semantic_regression_when_available(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            {
                "node_f1": 0.51,
                "relation_f1": 0.46,
                "llm_node_f1": 0.79,
                "llm_relation_f1": 0.56,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
        )

        self.assertFalse(payload["accepted"])
        self.assertFalse(payload["safety_gate"]["relation_not_significantly_worse"])

    def test_llm_judge_failures_block_acceptance(self) -> None:
        payload = decision(
            {
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "llm_element_evaluated": 10.0,
                "llm_element_failed": 0.0,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
            },
            {
                "llm_node_f1": 0.83,
                "llm_relation_f1": 0.73,
                "llm_node_precision": 0.90,
                "llm_relation_precision": 0.90,
                "llm_element_evaluated": 9.0,
                "llm_element_failed": 1.0,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
            },
        )

        self.assertFalse(payload["accepted"])
        self.assertFalse(payload["safety_gate"]["llm_judge_failures_not_increased"])

    def test_prompt_size_uses_absolute_char_limit_only(self) -> None:
        baseline = {
            "node_f1": 0.50,
            "relation_f1": 0.40,
            "llm_node_f1": 0.50,
            "llm_relation_f1": 0.40,
            "llm_node_precision": 0.80,
            "llm_relation_precision": 0.80,
            "llm_element_evaluated": 10.0,
            "plantuml_compilation_pass_rate": 1.0,
            "infrastructure_error_rate": 0.0,
        }
        candidate = {
            "node_f1": 0.56,
            "relation_f1": 0.46,
            "llm_node_f1": 0.56,
            "llm_relation_f1": 0.46,
            "llm_node_precision": 0.80,
            "llm_relation_precision": 0.80,
            "llm_element_evaluated": 10.0,
            "plantuml_compilation_pass_rate": 1.0,
            "infrastructure_error_rate": 0.0,
        }

        payload = decision(
            baseline,
            candidate,
            allow_bootstrap=True,
            baseline_prompt="1234567890",
            candidate_prompt="x" * 45,
            max_prompt_chars=100,
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["acceptance_mode"], "standard")
        self.assertTrue(payload["prompt_growth"]["prompt_size_ok"])

        payload = decision(
            baseline,
            candidate,
            allow_bootstrap=True,
            baseline_prompt="1234567890",
            candidate_prompt="x" * 45,
            max_prompt_chars=40,
        )

        self.assertFalse(payload["accepted"])
        self.assertFalse(payload["prompt_growth"]["prompt_size_ok"])
        self.assertIn("bootstrap_gate", payload["rejection_reasons"])

    def test_standard_gate_rejects_precision_regression(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "node_precision": 0.80,
                "relation_precision": 0.80,
                "llm_node_f1": 0.50,
                "llm_relation_f1": 0.40,
                "llm_node_precision": 0.80,
                "llm_relation_precision": 0.80,
                "llm_element_evaluated": 10.0,
                "plantuml_compilation_pass_rate": 1.0,
                "syntax_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
            },
            {
                "node_f1": 0.50,
                "relation_f1": 0.43,
                "node_precision": 0.75,
                "relation_precision": 0.80,
                "llm_node_f1": 0.50,
                "llm_relation_f1": 0.43,
                "llm_node_precision": 0.75,
                "llm_relation_precision": 0.80,
                "llm_element_evaluated": 10.0,
                "plantuml_compilation_pass_rate": 1.0,
                "syntax_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
            },
        )

        self.assertFalse(payload["accepted"])
        self.assertFalse(payload["safety_gate"]["node_precision_not_significantly_worse"])

    def test_bootstrap_allows_small_compile_drop_for_strong_semantic_gain(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "llm_node_f1": 0.50,
                "llm_relation_f1": 0.40,
                "llm_node_precision": 0.80,
                "llm_relation_precision": 0.80,
                "llm_element_evaluated": 10.0,
                "plantuml_compilation_pass_rate": 1.0,
                "syntax_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
            },
            {
                "node_f1": 0.56,
                "relation_f1": 0.46,
                "llm_node_f1": 0.56,
                "llm_relation_f1": 0.46,
                "llm_node_precision": 0.80,
                "llm_relation_precision": 0.80,
                "llm_element_evaluated": 10.0,
                "plantuml_compilation_pass_rate": 0.92,
                "syntax_pass_rate": 0.92,
                "infrastructure_error_rate": 0.0,
            },
            allow_bootstrap=True,
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["acceptance_mode"], "bootstrap")
        self.assertFalse(payload["safety_gate"]["compile_not_significantly_worse"])


if __name__ == "__main__":
    unittest.main()
