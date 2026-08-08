import unittest

from run import any_improvement_decision, two_stage_gate_decision


def repeat_summary(
    *,
    node: float,
    relation: float,
    compile_rate: float,
    syntax_rate: float | None = None,
    evaluated: int = 30,
    failed: int = 0,
    infra: float = 0.0,
) -> dict[str, float]:
    return {
        "count": 30.0,
        "syntax_pass_rate": compile_rate if syntax_rate is None else syntax_rate,
        "llm_element_evaluated": float(evaluated),
        "llm_element_failed": float(failed),
        "llm_node_f1": node,
        "llm_relation_f1": relation,
        "plantuml_compilation_pass_rate": compile_rate,
        "infrastructure_error_rate": infra,
    }


def positive_cross_dataset_results(metrics):
    return {
        metric: {
            "available": True,
            "balanced_mean_delta": 0.01,
            "source_weighted_mean_delta": 0.01,
            "weight_basis": "source_population",
            "missing_datasets": [],
            "source_dataset_count_missing": False,
        }
        for metric in metrics
    }


class AnyImprovementGateTest(unittest.TestCase):
    def decide(
        self,
        baseline,
        candidate,
        *,
        family="semantic",
        required_metrics=("llm_node_f1",),
        **overrides,
    ):
        kwargs = {
            "baseline_summaries": baseline,
            "candidate_summaries": candidate,
            "validation_case_count": 30,
            "candidate_prompt": "candidate",
            "baseline_prompt": "baseline",
            "max_prompt_chars": 100,
            "candidate_evidence_family": family,
            "required_metrics": required_metrics,
            "cross_dataset_metric_results": positive_cross_dataset_results(
                required_metrics
            ),
        }
        kwargs.update(overrides)
        accepted, payload = any_improvement_decision(**kwargs)
        self.assertEqual(accepted, payload["accepted"])
        return payload

    def test_node_candidate_accepts_positive_node_without_regression_floor(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.7001, relation=0.30, compile_rate=0.40)
            for _ in range(3)
        ]

        payload = self.decide(baseline, candidate)

        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["acceptance_policy"],
            "all-required-positive-pooled-balanced-and-source-weighted-mean-delta",
        )
        self.assertEqual(payload["required_metrics"], ["llm_node_f1"])
        self.assertEqual(payload["winning_metrics"], ["llm_node_f1"])
        self.assertGreater(payload["metric_results"]["llm_node_f1"]["mean_delta"], 0.0)
        self.assertNotIn("min_delta", payload["metric_results"]["llm_node_f1"])
        self.assertNotIn("min_wins", payload["metric_results"]["llm_node_f1"])
        self.assertNotIn("semantic_safety_results", payload)
        self.assertNotIn("compile_safety_results", payload)

    def test_node_candidate_cannot_use_relation_gain_as_substitute(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.60, relation=0.80, compile_rate=0.90)
            for _ in range(3)
        ]

        payload = self.decide(baseline, candidate)

        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["non_improving_required_metrics"], ["llm_node_f1"]
        )
        self.assertEqual(
            payload["rejection_reasons"], ["required_metric_not_improved"]
        )

    def test_relation_candidate_cannot_use_node_gain_as_substitute(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.80, relation=0.60, compile_rate=0.90)
            for _ in range(3)
        ]

        payload = self.decide(
            baseline,
            candidate,
            required_metrics=("llm_relation_f1",),
        )

        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["non_improving_required_metrics"], ["llm_relation_f1"]
        )

    def test_mixed_semantic_candidate_requires_both_metrics(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.75, relation=0.69, compile_rate=0.90)
            for _ in range(3)
        ]

        payload = self.decide(
            baseline,
            candidate,
            required_metrics=("llm_node_f1", "llm_relation_f1"),
        )

        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["winning_metrics"], ["llm_node_f1"])
        self.assertEqual(
            payload["non_improving_required_metrics"], ["llm_relation_f1"]
        )
        self.assertIsNone(payload["direct_metric"])
        self.assertEqual(payload["direct_metric_results"], {})

    def test_required_metric_does_not_require_positive_every_repeat(self):
        baseline = [
            repeat_summary(node=0.50, relation=0.50, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.80, relation=0.50, compile_rate=0.90),
            repeat_summary(node=0.40, relation=0.50, compile_rate=0.90),
            repeat_summary(node=0.40, relation=0.50, compile_rate=0.90),
        ]

        payload = self.decide(baseline, candidate)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["metric_results"]["llm_node_f1"]["wins"], 1)
        self.assertGreater(payload["metric_results"]["llm_node_f1"]["mean_delta"], 0.0)

    def test_exact_zero_required_metric_is_rejected(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.70, relation=0.80, compile_rate=0.99)
            for _ in range(3)
        ]

        payload = self.decide(baseline, candidate)

        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["rejection_reasons"], ["required_metric_not_improved"]
        )

    def test_balanced_positive_but_source_weighted_negative_is_rejected(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.71, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        cross_dataset = positive_cross_dataset_results(("llm_node_f1",))
        cross_dataset["llm_node_f1"]["source_weighted_mean_delta"] = -0.001

        payload = self.decide(
            baseline,
            candidate,
            cross_dataset_metric_results=cross_dataset,
        )

        self.assertTrue(payload["evaluation_valid"])
        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["rejection_reasons"],
            ["required_metric_source_weighted_not_improved"],
        )

    def test_balanced_and_source_weighted_positive_are_accepted(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.71, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]

        payload = self.decide(baseline, candidate)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["rejection_reasons"], [])

    def test_missing_source_count_is_invalid(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.71, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        cross_dataset = positive_cross_dataset_results(("llm_node_f1",))
        cross_dataset["llm_node_f1"].update(
            {
                "available": False,
                "balanced_mean_delta": None,
                "source_weighted_mean_delta": None,
                "source_dataset_count_missing": True,
                "missing_count_datasets": ["rac"],
            }
        )

        payload = self.decide(
            baseline,
            candidate,
            cross_dataset_metric_results=cross_dataset,
        )

        self.assertFalse(payload["evaluation_valid"])
        self.assertEqual(payload["invalid_reasons"], ["source_dataset_count_missing"])

    def test_missing_required_source_dataset_measurement_is_invalid(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.71, relation=0.70, compile_rate=0.90)
            for _ in range(3)
        ]
        cross_dataset = positive_cross_dataset_results(("llm_node_f1",))
        cross_dataset["llm_node_f1"].update(
            {
                "available": False,
                "balanced_mean_delta": None,
                "source_weighted_mean_delta": None,
                "missing_datasets": ["pure"],
            }
        )

        payload = self.decide(
            baseline,
            candidate,
            cross_dataset_metric_results=cross_dataset,
        )

        self.assertFalse(payload["evaluation_valid"])
        self.assertEqual(payload["invalid_reasons"], ["required_metric_incomplete"])

    def test_compile_accepts_direct_gain_without_semantic_safety_check(self):
        baseline = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.80)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.20, relation=0.20, compile_rate=0.8001)
            for _ in range(3)
        ]

        payload = self.decide(
            baseline,
            candidate,
            family="compile",
            required_metrics=("plantuml_compilation_pass_rate",),
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["acceptance_policy"],
            "all-required-positive-pooled-balanced-and-source-weighted-mean-delta",
        )
        self.assertEqual(
            payload["direct_metric"], "plantuml_compilation_pass_rate"
        )

    def test_compile_rejects_when_direct_metric_does_not_improve(self):
        baseline = [
            repeat_summary(node=0.50, relation=0.50, compile_rate=0.80)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.60, relation=0.60, compile_rate=0.80, syntax_rate=0.90)
            for _ in range(3)
        ]

        payload = self.decide(
            baseline,
            candidate,
            family="compile",
            required_metrics=("plantuml_compilation_pass_rate",),
        )

        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["rejection_reasons"], ["required_metric_not_improved"]
        )

    def test_missing_semantic_measurement_is_invalid(self):
        baseline = [
            repeat_summary(node=0.50, relation=0.50, compile_rate=0.80)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.60, relation=0.50, compile_rate=0.80, evaluated=0, failed=30)
            for _ in range(3)
        ]

        payload = self.decide(baseline, candidate)

        self.assertFalse(payload["evaluation_valid"])
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["invalid_reasons"], ["required_metric_incomplete"])
        self.assertEqual(payload["incomplete_required_metrics"], ["llm_node_f1"])

    def test_missing_required_metric_key_is_invalid_not_zero(self):
        baseline = [
            repeat_summary(node=0.50, relation=0.50, compile_rate=0.80)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.60, relation=0.60, compile_rate=0.80)
            for _ in range(3)
        ]
        candidate[1].pop("llm_node_f1")

        payload = self.decide(baseline, candidate)

        self.assertFalse(payload["evaluation_valid"])
        self.assertEqual(payload["incomplete_required_metrics"], ["llm_node_f1"])
        self.assertIsNone(
            payload["required_metric_results"]["llm_node_f1"]["mean_delta"]
        )
        self.assertEqual(
            payload["required_metric_results"]["llm_node_f1"]["repeat_deltas"],
            [],
        )

    def test_missing_compile_measurement_is_invalid_for_compile_candidate(self):
        baseline = [
            repeat_summary(node=0.50, relation=0.50, compile_rate=0.80)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.50, relation=0.50, compile_rate=0.80)
            for _ in range(3)
        ]
        for summary in [*baseline, *candidate]:
            summary.pop("plantuml_compilation_pass_rate")

        payload = self.decide(
            baseline,
            candidate,
            family="compile",
            required_metrics=("plantuml_compilation_pass_rate",),
        )

        self.assertFalse(payload["evaluation_valid"])
        self.assertIn("required_metric_incomplete", payload["invalid_reasons"])

    def test_prompt_size_and_infrastructure_are_validity_failures(self):
        baseline = [
            repeat_summary(node=0.50, relation=0.50, compile_rate=0.80, infra=0.1)
            for _ in range(3)
        ]
        candidate = [
            repeat_summary(node=0.60, relation=0.50, compile_rate=0.80)
            for _ in range(3)
        ]

        payload = self.decide(
            baseline,
            candidate,
            candidate_prompt="x" * 101,
        )

        self.assertFalse(payload["evaluation_valid"])
        self.assertIn("prompt_too_long", payload["invalid_reasons"])
        self.assertIn("infrastructure_error", payload["invalid_reasons"])

    def test_two_stage_gate_preserves_gate2_measurement_failure(self):
        payload = two_stage_gate_decision(
            gate1_decision={
                "accepted": True,
                "evaluation_valid": True,
                "invalid_reasons": [],
                "rejection_reasons": [],
            },
            gate2_decision={
                "accepted": False,
                "evaluation_valid": False,
                "invalid_reasons": ["infrastructure_error"],
                "rejection_reasons": ["evaluation_invalid"],
            },
            gate2_required=True,
        )

        self.assertFalse(payload["evaluation_valid"])
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["invalid_reasons"], ["gate2:infrastructure_error"])
        self.assertEqual(payload["rejection_reasons"][0], "gate2_rejected")

    def test_two_stage_gate_requires_both_positive_decisions(self):
        gate = {
            "accepted": True,
            "evaluation_valid": True,
            "invalid_reasons": [],
            "rejection_reasons": [],
            "candidate_evidence_family": "semantic",
            "required_metrics": ["llm_node_f1"],
        }
        rejected_gate2 = {
            **gate,
            "accepted": False,
            "rejection_reasons": ["required_metric_not_improved"],
        }

        payload = two_stage_gate_decision(
            gate1_decision=gate,
            gate2_decision=rejected_gate2,
            gate2_required=True,
        )

        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["acceptance_policy"],
            "all-required-positive-pooled-balanced-and-source-weighted-mean-delta",
        )
        self.assertEqual(
            payload["gate_sequence_policy"], "gate1-then-fresh-gate2"
        )
        self.assertEqual(
            payload["rejection_reasons"],
            ["gate2_rejected", "required_metric_not_improved"],
        )

    def test_single_gate_uses_gate1_decision_and_records_policy(self):
        gate = {
            "accepted": True,
            "evaluation_valid": True,
            "invalid_reasons": [],
            "rejection_reasons": [],
            "candidate_evidence_family": "semantic",
            "required_metrics": ["llm_node_f1"],
        }
        payload = two_stage_gate_decision(
            gate1_decision=gate,
            gate2_decision=None,
            gate2_required=False,
        )

        self.assertTrue(payload["accepted"])
        self.assertTrue(payload["evaluation_valid"])
        self.assertEqual(payload["gate_sequence_policy"], "single-gate1")
        self.assertFalse(payload["gate2_required"])
        self.assertFalse(payload["gate2_evaluated"])

    def test_required_metrics_must_be_non_empty_and_match_family(self):
        summaries = [
            repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)
        ]

        with self.assertRaisesRegex(ValueError, "must not be empty"):
            self.decide(summaries, summaries, required_metrics=())
        with self.assertRaisesRegex(ValueError, "incompatible"):
            self.decide(
                summaries,
                summaries,
                required_metrics=("plantuml_compilation_pass_rate",),
            )


if __name__ == "__main__":
    unittest.main()
