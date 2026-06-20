import unittest

from run import acceptance_decision


def decision(
    baseline_summary: dict[str, float],
    candidate_summary: dict[str, float],
    *,
    metric_source: str,
) -> dict:
    accepted, payload = acceptance_decision(
        iteration=2,
        baseline_summary=baseline_summary,
        candidate_summary=candidate_summary,
        candidate_prompt="candidate",
        baseline_prompt="baseline",
        max_prompt_growth_ratio=6.0,
        max_prompt_chars=9000,
        min_relation_delta=-0.15,
        min_node_delta=-0.15,
        min_compile_delta=-0.10,
        relation_accept_delta=0.03,
        node_accept_delta=0.03,
        compile_accept_delta=0.10,
        metric_source=metric_source,
    )
    payload["accepted"] = accepted
    return payload


class AcceptanceGateTest(unittest.TestCase):
    def test_deterministic_mode_uses_embedding_metrics(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            {
                "node_f1": 0.50,
                "relation_f1": 0.44,
                "llm_node_f1": 0.70,
                "llm_relation_f1": 0.62,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            metric_source="deterministic",
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["acceptance_relation_metric"], "relation_f1")

    def test_llm_mode_uses_llm_metrics_for_benefit(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            {
                "node_f1": 0.50,
                "relation_f1": 0.44,
                "llm_node_f1": 0.70,
                "llm_relation_f1": 0.62,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            metric_source="llm",
        )

        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["acceptance_relation_metric"], "llm_relation_f1")

    def test_hybrid_mode_blocks_large_llm_regression(self) -> None:
        payload = decision(
            {
                "node_f1": 0.50,
                "relation_f1": 0.40,
                "llm_node_f1": 0.80,
                "llm_relation_f1": 0.70,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            {
                "node_f1": 0.51,
                "relation_f1": 0.46,
                "llm_node_f1": 0.79,
                "llm_relation_f1": 0.56,
                "plantuml_compilation_pass_rate": 1.0,
                "infrastructure_error_rate": 0.0,
                "llm_element_evaluated": 10.0,
            },
            metric_source="hybrid",
        )

        self.assertFalse(payload["accepted"])
        self.assertFalse(payload["safety_gate"]["llm_semantic_guard_ok"])


if __name__ == "__main__":
    unittest.main()
