import unittest

from run import acceptance_decision, any_improvement_decision


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


def repeat_summary(*, node: float, relation: float, compile_rate: float, evaluated: int = 30, failed: int = 0, infra: float = 0.0) -> dict[str, float]:
    return {
        "count": 30.0,
        "llm_element_evaluated": float(evaluated),
        "llm_element_failed": float(failed),
        "llm_node_f1": node,
        "llm_relation_f1": relation,
        "plantuml_compilation_pass_rate": compile_rate,
        "infrastructure_error_rate": infra,
    }


class AnyImprovementGateTest(unittest.TestCase):
    def decide(self, baseline, candidate, **overrides):
        kwargs = {
            "baseline_summaries": baseline,
            "candidate_summaries": candidate,
            "validation_case_count": 30,
            "candidate_prompt": "candidate",
            "baseline_prompt": "baseline",
            "max_prompt_chars": 100,
            "min_wins": 2,
            "min_deltas": {
                "llm_node_f1": 0.0,
                "llm_relation_f1": 0.0,
            },
        }
        kwargs.update(overrides)
        accepted, payload = any_improvement_decision(**kwargs)
        self.assertEqual(accepted, payload["accepted"])
        return payload

    def test_node_gain_accepts_despite_relation_and_compile_regression(self):
        baseline = [repeat_summary(node=0.7, relation=0.7, compile_rate=1.0) for _ in range(3)]
        candidate = [
            repeat_summary(node=node, relation=0.3, compile_rate=0.5)
            for node in (0.72, 0.71, 0.69)
        ]
        payload = self.decide(baseline, candidate)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["winning_metrics"], ["llm_node_f1"])

    def test_relation_gain_accepts_despite_other_regressions(self):
        baseline = [repeat_summary(node=0.8, relation=0.6, compile_rate=1.0) for _ in range(3)]
        candidate = [
            repeat_summary(node=0.4, relation=relation, compile_rate=0.5)
            for relation in (0.62, 0.63, 0.59)
        ]
        self.assertTrue(self.decide(baseline, candidate)["accepted"])

    def test_compile_gain_cannot_win_when_judge_metrics_are_unavailable(self):
        baseline = [repeat_summary(node=0.0, relation=0.0, compile_rate=0.8, evaluated=0, failed=30) for _ in range(3)]
        candidate = [
            repeat_summary(node=0.0, relation=0.0, compile_rate=value, evaluated=0, failed=30)
            for value in (0.9, 0.9, 0.7)
        ]
        payload = self.decide(baseline, candidate)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["winning_metrics"], [])
        self.assertIn("no_complete_acceptance_metric", payload["invalid_reasons"])
        for actual, expected in zip(
            payload["diagnostic_repeat_deltas"]["plantuml_compilation_pass_rate"],
            [0.1, 0.1, -0.1],
        ):
            self.assertAlmostEqual(actual, expected)

    def test_compile_gain_is_diagnostic_when_semantic_metrics_do_not_improve(self):
        baseline = [repeat_summary(node=0.7, relation=0.6, compile_rate=0.8) for _ in range(3)]
        candidate = [repeat_summary(node=0.7, relation=0.6, compile_rate=0.9) for _ in range(3)]
        payload = self.decide(baseline, candidate)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["rejection_reasons"], ["no_stable_improvement"])
        self.assertEqual(payload["winning_metrics"], [])
        self.assertNotIn("plantuml_compilation_pass_rate", payload["metric_results"])

    def test_only_one_positive_repeat_is_rejected(self):
        baseline = [repeat_summary(node=0.7, relation=0.7, compile_rate=1.0) for _ in range(3)]
        candidate = [
            repeat_summary(node=node, relation=0.7, compile_rate=1.0)
            for node in (0.73, 0.69, 0.69)
        ]
        payload = self.decide(baseline, candidate)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["rejection_reasons"], ["no_stable_improvement"])

    def test_two_positive_repeats_still_require_mean_above_min_delta(self):
        baseline = [repeat_summary(node=0.7, relation=0.7, compile_rate=1.0) for _ in range(3)]
        candidate = [
            repeat_summary(node=node, relation=0.7, compile_rate=1.0)
            for node in (0.73, 0.73, 0.69)
        ]
        payload = self.decide(
            baseline,
            candidate,
            min_deltas={
                "llm_node_f1": 0.03,
                "llm_relation_f1": 0.0,
            },
        )
        self.assertFalse(payload["accepted"])

    def test_prompt_size_and_infrastructure_are_validity_failures(self):
        baseline = [repeat_summary(node=0.7, relation=0.7, compile_rate=1.0) for _ in range(3)]
        candidate = [repeat_summary(node=0.8, relation=0.7, compile_rate=1.0) for _ in range(3)]
        oversized = self.decide(baseline, candidate, candidate_prompt="x" * 101)
        self.assertFalse(oversized["accepted"])
        self.assertIn("prompt_too_long", oversized["invalid_reasons"])
        candidate[1]["infrastructure_error_rate"] = 1 / 30
        infra = self.decide(baseline, candidate)
        self.assertFalse(infra["accepted"])
        self.assertIn("infrastructure_error", infra["invalid_reasons"])

    def test_historical_single_summary_replay_matches_disjunctive_semantics(self):
        historical = [
            (0.743523, 0.501193, 1.0, 0.783547, 0.531133, 0.933333),
            (0.777590, 0.553167, 1.0, 0.792780, 0.530207, 0.966667),
            (0.780733, 0.525273, 0.966667, 0.771190, 0.537777, 0.933333),
        ]
        for base_node, base_relation, base_compile, cand_node, cand_relation, cand_compile in historical:
            payload = self.decide(
                [repeat_summary(node=base_node, relation=base_relation, compile_rate=base_compile)],
                [repeat_summary(node=cand_node, relation=cand_relation, compile_rate=cand_compile)],
                min_wins=1,
            )
            self.assertTrue(payload["accepted"])

    def test_latest_compile_only_run_replays_as_rejected(self):
        baseline = [
            repeat_summary(node=node, relation=relation, compile_rate=compile_rate, evaluated=20)
            for node, relation, compile_rate in (
                (0.771875, 0.496710, 0.95),
                (0.826955, 0.610505, 0.90),
                (0.851015, 0.604635, 0.90),
            )
        ]
        candidate = [
            repeat_summary(node=node, relation=relation, compile_rate=compile_rate, evaluated=20)
            for node, relation, compile_rate in (
                (0.815650, 0.546045, 0.95),
                (0.792625, 0.531160, 1.00),
                (0.812435, 0.529725, 1.00),
            )
        ]
        payload = self.decide(
            baseline,
            candidate,
            validation_case_count=20,
            min_deltas={
                "llm_node_f1": 0.018995682402974327,
                "llm_relation_f1": 0.052784916598080704,
            },
        )
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["winning_metrics"], [])
        self.assertEqual(payload["metric_results"]["llm_node_f1"]["wins"], 1)
        self.assertEqual(payload["metric_results"]["llm_relation_f1"]["wins"], 1)
        self.assertGreater(
            sum(payload["diagnostic_repeat_deltas"]["plantuml_compilation_pass_rate"]),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
