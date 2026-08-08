import unittest

from llm_element_metrics import CompilationResult, LLMElementMetrics, PRF
from metrics import EvaluationRecord, SyntaxResult, empty_metric_bundle
from run import (
    aggregate_source_dataset_metrics,
    any_improvement_decision,
    per_dataset_metric_decomposition,
    two_stage_gate_decision,
)


def record(
    *,
    dataset: str,
    case_id: str,
    node_f1: float,
    relation_f1: float = 0.5,
    compiled: bool = True,
) -> EvaluationRecord:
    return EvaluationRecord(
        dataset=dataset,
        case_id=case_id,
        input_requirement="The user opens the database.",
        gold_plantuml="@startuml\n:Open database;\n@enduml",
        generated_plantuml="@startuml\nstart\n@enduml",
        syntax=SyntaxResult(True, []),
        node_metrics=empty_metric_bundle(),
        relation_metrics=empty_metric_bundle(),
        plantuml_compilation=CompilationResult(compiled, [] if compiled else ["boom"]),
        llm_element_metrics=LLMElementMetrics(
            enabled=True,
            status="success",
            node_metrics=PRF(node_f1, node_f1, node_f1),
            relation_metrics=PRF(relation_f1, relation_f1, relation_f1),
            gt_elements={},
            pred_elements={},
            matching={},
            counts={},
        ),
        failure_types=[],
    )


def repeat_summary(*, node: float, relation: float, compile_rate: float) -> dict[str, float]:
    return {
        "count": 30.0,
        "syntax_pass_rate": compile_rate,
        "llm_element_evaluated": 30.0,
        "llm_element_failed": 0.0,
        "llm_node_f1": node,
        "llm_relation_f1": relation,
        "plantuml_compilation_pass_rate": compile_rate,
        "infrastructure_error_rate": 0.0,
    }


class PerDatasetDecompositionTest(unittest.TestCase):
    def test_decomposition_separates_opposing_dataset_effects(self):
        """A pooled mean near zero can hide a large win plus a large loss."""

        baseline = [
            record(dataset="bp", case_id="bp-1", node_f1=0.70),
            record(dataset="us", case_id="us-1", node_f1=0.95),
        ]
        candidate = [
            record(dataset="bp", case_id="bp-1", node_f1=0.80),
            record(dataset="us", case_id="us-1", node_f1=0.85),
        ]

        decomposition = per_dataset_metric_decomposition([(1, baseline, candidate)])

        self.assertEqual(sorted(decomposition), ["bp", "us"])
        bp_delta = decomposition["bp"]["metrics"]["llm_node_f1"]["mean_delta"]
        us_delta = decomposition["us"]["metrics"]["llm_node_f1"]["mean_delta"]
        self.assertTrue(
            decomposition["bp"]["metrics"]["llm_node_f1"]["available"]
        )
        self.assertEqual(
            decomposition["bp"]["metrics"]["llm_node_f1"]["missing_repeats"],
            [],
        )
        self.assertAlmostEqual(bp_delta, 0.10, places=6)
        self.assertAlmostEqual(us_delta, -0.10, places=6)
        # The pooled mean cancels out; the decomposition is what makes the
        # conflict visible.
        self.assertAlmostEqual(bp_delta + us_delta, 0.0, places=6)

    def test_case_counts_and_repeat_counts_are_per_dataset(self):
        baseline = [
            record(dataset="fsd", case_id="fsd-1", node_f1=0.60),
            record(dataset="fsd", case_id="fsd-2", node_f1=0.60),
            record(dataset="rac", case_id="rac-1", node_f1=0.60),
        ]
        candidate = [
            record(dataset="fsd", case_id="fsd-1", node_f1=0.70),
            record(dataset="fsd", case_id="fsd-2", node_f1=0.70),
            record(dataset="rac", case_id="rac-1", node_f1=0.60),
        ]

        decomposition = per_dataset_metric_decomposition(
            [(1, baseline, candidate), (2, baseline, candidate)]
        )

        self.assertEqual(decomposition["fsd"]["case_count"], 2)
        self.assertEqual(decomposition["rac"]["case_count"], 1)
        self.assertEqual(decomposition["fsd"]["repeat_count"], 2)
        fsd_deltas = decomposition["fsd"]["metrics"]["llm_node_f1"]["repeat_deltas"]
        self.assertEqual(len(fsd_deltas), 2)
        for delta in fsd_deltas:
            self.assertAlmostEqual(delta, 0.10, places=6)
        self.assertEqual(decomposition["fsd"]["metrics"]["llm_node_f1"]["wins"], 2)
        self.assertEqual(decomposition["rac"]["metrics"]["llm_node_f1"]["wins"], 0)

    def test_single_dataset_gate_decomposition_matches_pooled_delta(self):
        """With a homogeneous gate the effect is not diluted."""

        baseline = [
            record(dataset="fsd", case_id=f"fsd-{i}", node_f1=0.60) for i in range(4)
        ]
        candidate = [
            record(dataset="fsd", case_id=f"fsd-{i}", node_f1=0.70) for i in range(4)
        ]

        decomposition = per_dataset_metric_decomposition([(1, baseline, candidate)])

        self.assertEqual(list(decomposition), ["fsd"])
        self.assertAlmostEqual(
            decomposition["fsd"]["metrics"]["llm_node_f1"]["mean_delta"],
            0.10,
            places=6,
        )

    def test_compile_metric_is_decomposed(self):
        baseline = [
            record(dataset="bp", case_id="bp-1", node_f1=0.5, compiled=False),
            record(dataset="us", case_id="us-1", node_f1=0.5, compiled=True),
        ]
        candidate = [
            record(dataset="bp", case_id="bp-1", node_f1=0.5, compiled=True),
            record(dataset="us", case_id="us-1", node_f1=0.5, compiled=True),
        ]

        decomposition = per_dataset_metric_decomposition([(1, baseline, candidate)])

        self.assertAlmostEqual(
            decomposition["bp"]["metrics"]["plantuml_compilation_pass_rate"][
                "mean_delta"
            ],
            1.0,
            places=6,
        )
        self.assertAlmostEqual(
            decomposition["us"]["metrics"]["plantuml_compilation_pass_rate"][
                "mean_delta"
            ],
            0.0,
            places=6,
        )

    def test_missing_paired_dataset_is_unavailable_instead_of_zero(self):
        baseline = [
            record(dataset="bp", case_id="bp-1", node_f1=0.5),
        ]
        candidate = [
            record(dataset="us", case_id="us-1", node_f1=0.8),
        ]

        decomposition = per_dataset_metric_decomposition(
            [(1, baseline, candidate)]
        )

        for dataset in ("bp", "us"):
            metric = decomposition[dataset]["metrics"]["llm_node_f1"]
            self.assertFalse(metric["available"])
            self.assertEqual(metric["repeat_deltas"], [])
            self.assertIsNone(metric["mean_delta"])
            self.assertIsNone(metric["wins"])
            self.assertEqual(metric["missing_repeats"], [1])

    def test_empty_repeat_pairs_yield_empty_decomposition(self):
        self.assertEqual(per_dataset_metric_decomposition([]), {})


class SourceDatasetAggregationTest(unittest.TestCase):
    def test_balanced_and_source_weighted_are_computed_from_source_population(self):
        per_dataset = {
            "small": {
                "metrics": {
                    "llm_node_f1": {"available": True, "mean_delta": 0.10}
                }
            },
            "large": {
                "metrics": {
                    "llm_node_f1": {"available": True, "mean_delta": -0.01}
                }
            },
        }
        result = aggregate_source_dataset_metrics(
            per_dataset_results=per_dataset,
            source_dataset_counts={"small": 10, "large": 90},
            metrics=("llm_node_f1",),
        )["llm_node_f1"]

        self.assertTrue(result["available"])
        self.assertAlmostEqual(result["balanced_mean_delta"], 0.045)
        self.assertAlmostEqual(result["source_weighted_mean_delta"], 0.001)
        self.assertEqual(result["weight_basis"], "source_population")

    def test_missing_source_dataset_is_incomplete_not_zero_filled(self):
        result = aggregate_source_dataset_metrics(
            per_dataset_results={
                "bp": {
                    "metrics": {
                        "llm_node_f1": {"available": True, "mean_delta": 0.1}
                    }
                }
            },
            source_dataset_counts={"bp": 10, "fsd": 10},
            metrics=("llm_node_f1",),
        )["llm_node_f1"]

        self.assertFalse(result["available"])
        self.assertEqual(result["missing_datasets"], ["fsd"])
        self.assertIsNone(result["balanced_mean_delta"])


class AcceptanceIsolationTest(unittest.TestCase):
    """Acceptance consumes only compact source-dataset aggregates.

    Raw records, full decomposition, group diagnostics, and heldout evidence stay
    outside the numeric decision boundary.
    """

    @staticmethod
    def compact_result(delta: float = 0.05) -> dict[str, dict[str, object]]:
        return {
            "llm_node_f1": {
                "available": True,
                "balanced_mean_delta": delta,
                "source_weighted_mean_delta": delta,
                "weight_basis": "source_population",
                "missing_datasets": [],
                "source_dataset_count_missing": False,
            }
        }

    def test_any_improvement_decision_rejects_per_dataset_argument(self):
        baseline = [repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)]
        candidate = [repeat_summary(node=0.75, relation=0.70, compile_rate=0.90)]

        with self.assertRaises(TypeError):
            any_improvement_decision(
                baseline_summaries=baseline,
                candidate_summaries=candidate,
                validation_case_count=30,
                candidate_prompt="candidate",
                baseline_prompt="baseline",
                max_prompt_chars=100,
                candidate_evidence_family="semantic",
                required_metrics=("llm_node_f1",),
                cross_dataset_metric_results=self.compact_result(),
                per_dataset_metric_results={"bp": {}},
            )

    def test_acceptance_rejects_group_diagnostics_and_heldout_arguments(self):
        baseline = [repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)]
        candidate = [repeat_summary(node=0.75, relation=0.70, compile_rate=0.90)]
        common = {
            "baseline_summaries": baseline,
            "candidate_summaries": candidate,
            "validation_case_count": 30,
            "candidate_prompt": "candidate",
            "baseline_prompt": "baseline",
            "max_prompt_chars": 100,
            "candidate_evidence_family": "semantic",
            "required_metrics": ("llm_node_f1",),
            "cross_dataset_metric_results": self.compact_result(),
        }

        for field in ("group_diagnostics", "heldout_metric_results"):
            with self.subTest(field=field), self.assertRaises(TypeError):
                any_improvement_decision(**common, **{field: {}})

    def test_decision_payload_has_compact_but_no_raw_per_dataset_key(self):
        baseline = [repeat_summary(node=0.70, relation=0.70, compile_rate=0.90)]
        candidate = [repeat_summary(node=0.75, relation=0.70, compile_rate=0.90)]

        accepted, payload = any_improvement_decision(
            baseline_summaries=baseline,
            candidate_summaries=candidate,
            validation_case_count=30,
            candidate_prompt="candidate",
            baseline_prompt="baseline",
            max_prompt_chars=100,
            candidate_evidence_family="semantic",
            required_metrics=("llm_node_f1",),
            cross_dataset_metric_results=self.compact_result(),
        )

        self.assertTrue(accepted)
        self.assertNotIn("per_dataset_metric_results", payload)
        self.assertEqual(
            payload["cross_dataset_metric_results"], self.compact_result()
        )

    def test_two_stage_gate_passes_through_per_dataset_results(self):
        gate1 = {
            "accepted": True,
            "evaluation_valid": True,
            "invalid_reasons": [],
            "rejection_reasons": [],
            "metric_results": {},
            "per_dataset_metric_results": {"bp": {"case_count": 6}},
            "cross_dataset_metric_results": self.compact_result(0.01),
        }
        gate2 = {
            "accepted": True,
            "evaluation_valid": True,
            "invalid_reasons": [],
            "rejection_reasons": [],
            "metric_results": {},
            "per_dataset_metric_results": {"bp": {"case_count": 5}},
            "cross_dataset_metric_results": self.compact_result(0.02),
        }

        decision = two_stage_gate_decision(
            gate1_decision=gate1, gate2_decision=gate2, gate2_required=True
        )

        self.assertTrue(decision["accepted"])
        # Gate2 is the final evidence when it ran.
        self.assertEqual(
            decision["per_dataset_metric_results"], {"bp": {"case_count": 5}}
        )
        self.assertEqual(
            decision["gate1_decision"]["per_dataset_metric_results"],
            {"bp": {"case_count": 6}},
        )
        self.assertEqual(
            decision["cross_dataset_metric_results"], self.compact_result(0.02)
        )

    def test_missing_per_dataset_results_degrade_to_empty(self):
        gate1 = {
            "accepted": False,
            "evaluation_valid": True,
            "invalid_reasons": [],
            "rejection_reasons": ["required_metric_not_improved"],
        }

        decision = two_stage_gate_decision(
            gate1_decision=gate1, gate2_decision=None, gate2_required=True
        )

        self.assertEqual(decision["per_dataset_metric_results"], {})


if __name__ == "__main__":
    unittest.main()
