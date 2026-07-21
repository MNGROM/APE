import unittest
from pathlib import Path
from types import SimpleNamespace

from analysis.failure_analysis import failure_analysis_payload, matching_quality
from analysis.mechanism_clustering import (
    build_mechanism_observations,
    candidate_eligible_attributions,
    load_mechanism_taxonomy,
    sanitize_selected_failure_analysis,
    select_epoch_mechanism,
    validate_failure_analysis_payload,
)
from llm_element_metrics import CompilationResult, LLMElementMetrics, PRF
from metrics import EvaluationRecord, SyntaxResult, empty_metric_bundle


PROJECT_DIR = Path(__file__).resolve().parents[1]
TAXONOMY_V3_PATH = PROJECT_DIR / "prompt_workspace" / "mechanism_taxonomy_v3.json"
EVIDENCE_ID = "run:i001:b001:data:case-1"


def evidence(**overrides):
    item = {
        "evidence_id": EVIDENCE_ID,
        "dataset": "data",
        "case_id": "case-1",
        "requirement": "After startup, Task A and Task B run concurrently.",
        "llm_missing_nodes": [],
        "llm_extra_nodes": ["After startup"],
        "llm_missing_relations": ["Task A -> Task B (fork)"],
        "llm_extra_relations": [],
        "syntax_errors": [],
        "compile_errors": [],
        "syntax_passed": True,
        "plantuml_compiles": True,
        "matching_quality": {"status": "valid", "reasons": []},
    }
    item.update(overrides)
    return item


def context_attribution(*, trigger="temporal_context", **overrides):
    item = {
        "evidence_id": EVIDENCE_ID,
        "role": "primary",
        "requirement_quote": "After startup",
        "error_anchor": "After startup",
        "failure_direction": "activity_over_decomposition",
        "construct_family": "activity",
        "requirement_trigger": trigger,
        "gold_state": "none",
        "prediction_state": "single",
        "node_inventory_status": "not_applicable",
        "evidence_basis": "requirement_and_gold",
        "causal_rationale": "The temporal phrase was emitted as an unsupported activity.",
    }
    item.update(overrides)
    return item


def fork_attribution(**overrides):
    item = {
        "evidence_id": EVIDENCE_ID,
        "role": "primary",
        "requirement_quote": "Task A and Task B run concurrently",
        "error_anchor": "Task A -> Task B (fork)",
        "failure_direction": "missing_required_parallel",
        "construct_family": "fork",
        "requirement_trigger": "explicit_concurrency",
        "gold_state": "present",
        "prediction_state": "absent",
        "node_inventory_status": "sufficient",
        "evidence_basis": "requirement_and_gold",
        "causal_rationale": "Explicit concurrency is present but its fork relation is missing.",
    }
    item.update(overrides)
    return item


def atomic_payload(*items):
    return {"schema_version": "atomic-v1", "error_attributions": list(items)}


def evaluation_record(
    *,
    case_id: str,
    node_precision: float = 0.8,
    node_recall: float = 0.4,
    relation_precision: float = 0.7,
    relation_recall: float = 0.6,
    missing_nodes=None,
    extra_nodes=None,
    missing_relations=None,
    extra_relations=None,
    syntax_passed: bool = True,
    compile_passed: bool = True,
):
    llm_metrics = LLMElementMetrics(
        enabled=True,
        status="success",
        node_metrics=PRF(node_precision, node_recall, 0.0),
        relation_metrics=PRF(relation_precision, relation_recall, 0.0),
        gt_elements={},
        pred_elements={},
        matching={
            "nodes": {"tp": [], "fn": list(missing_nodes or []), "fp": list(extra_nodes or [])},
            "relations": {
                "tp": [],
                "fn": list(missing_relations or []),
                "fp": list(extra_relations or []),
            },
        },
        counts={},
    )
    return EvaluationRecord(
        dataset="data",
        case_id=case_id,
        input_requirement="Perform the stated actions.",
        gold_plantuml="@startuml\nstart\nstop\n@enduml",
        generated_plantuml="@startuml\nstart\nstop\n@enduml",
        syntax=SyntaxResult(syntax_passed, [] if syntax_passed else ["Unbalanced endif block"]),
        node_metrics=empty_metric_bundle(),
        relation_metrics=empty_metric_bundle(),
        plantuml_compilation=CompilationResult(
            compile_passed,
            [] if compile_passed else ["No valid @startuml wrapper found"],
        ),
        llm_element_metrics=llm_metrics,
        failure_types=["missing_activity"],
    )


class AtomicAttributionV3Test(unittest.TestCase):
    def setUp(self):
        self.taxonomy = load_mechanism_taxonomy(TAXONOMY_V3_PATH)

    def test_one_case_different_anchors_support_different_mechanisms(self):
        result = validate_failure_analysis_payload(
            atomic_payload(context_attribution(), fork_attribution()),
            evidence_catalog=[evidence()],
        )
        self.assertIsNotNone(result.normalized_payload)
        normalized = result.normalized_payload
        assert normalized is not None
        attributions = normalized["error_attributions"]
        self.assertEqual({item["anchor_kind"] for item in attributions}, {"extra_node", "missing_relation"})
        self.assertEqual(len({item["attribution_id"] for item in attributions}), 2)
        observations = build_mechanism_observations(
            normalized,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertEqual(
            {item["mechanism_id"] for item in observations},
            {"temporal_context_as_activity", "explicit_concurrency_not_mapped"},
        )

    def test_selected_atomic_evidence_removes_unselected_case_anchors(self):
        catalog = evidence(
            attribution_candidates=[
                {"anchor_kind": "extra_node", "error_anchor": "After startup"},
                {
                    "anchor_kind": "missing_relation",
                    "error_anchor": "Task A -> Task B (fork)",
                },
            ]
        )
        result = validate_failure_analysis_payload(
            atomic_payload(context_attribution(), fork_attribution()),
            evidence_catalog=[catalog],
        )
        assert result.normalized_payload is not None
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        selected = next(
            item
            for item in observations
            if item["mechanism_id"] == "temporal_context_as_activity"
        )
        sanitized = sanitize_selected_failure_analysis(selected)
        evidence_item = sanitized["evidence_catalog"][0]
        self.assertEqual(evidence_item["llm_extra_nodes"], ["After startup"])
        self.assertEqual(evidence_item["llm_missing_relations"], [])
        self.assertEqual(
            evidence_item["attribution_candidates"],
            [{"anchor_kind": "extra_node", "error_anchor": "After startup"}],
        )

    def test_atomic_anchor_budget_is_round_robin_across_cases(self):
        records = [
            evaluation_record(
                case_id="case-1",
                missing_nodes=["missing-1", "missing-2"],
                extra_nodes=["extra-1"],
                missing_relations=["a -> b (sequential)"],
            ),
            evaluation_record(
                case_id="case-2",
                missing_nodes=["missing-3", "missing-4"],
                extra_relations=["x -> y (sequential)"],
            ),
        ]
        payload = failure_analysis_payload(
            records,
            {"count": 2.0},
            atomic_anchor_budget=3,
        )
        self.assertEqual(payload["attribution_budget"], 3)
        counts = {
            item["case_id"]: len(item["attribution_candidates"])
            for item in payload["case_evidence"]
        }
        self.assertEqual(counts, {"case-1": 2, "case-2": 1})
        for case in payload["case_evidence"]:
            exposed = {
                anchor
                for field in (
                    "llm_missing_nodes",
                    "llm_extra_nodes",
                    "llm_missing_relations",
                    "llm_extra_relations",
                    "syntax_errors",
                    "compile_errors",
                )
                for anchor in case[field]
            }
            candidates = case["attribution_candidates"]
            self.assertEqual(exposed, {item["error_anchor"] for item in candidates})
            self.assertTrue(all(item["primary_allowed_by_matching"] for item in candidates))

    def test_atomic_anchor_admission_prioritizes_compiler_then_metric_deficit(self):
        compiler_record = evaluation_record(
            case_id="compile-case",
            node_precision=0.0,
            node_recall=0.0,
            missing_nodes=["missing-node"],
            syntax_passed=False,
            compile_passed=False,
        )
        payload = failure_analysis_payload(
            [compiler_record],
            {"count": 1.0},
            atomic_anchor_budget=2,
        )
        candidates = payload["case_evidence"][0]["attribution_candidates"]
        self.assertEqual(
            [item["anchor_kind"] for item in candidates],
            ["compile_error", "syntax_error"],
        )
        self.assertEqual(
            candidates[0]["allowed_primary_failure_directions"],
            ["syntax_or_format_error"],
        )

    def test_legacy_failure_payload_does_not_apply_atomic_budget(self):
        record = evaluation_record(
            case_id="legacy-case",
            missing_nodes=["missing-1", "missing-2"],
        )
        payload = failure_analysis_payload([record], {"count": 1.0})
        self.assertNotIn("attribution_budget", payload)
        self.assertNotIn("attribution_candidates", payload["case_evidence"][0])
        self.assertEqual(payload["case_evidence"][0]["llm_missing_nodes"], ["missing-1", "missing-2"])

    def test_invalid_anchor_is_isolated_without_rejecting_other_case_anchor(self):
        invalid = context_attribution(error_anchor="fabricated anchor")
        result = validate_failure_analysis_payload(
            atomic_payload(invalid, fork_attribution()),
            evidence_catalog=[evidence()],
        )
        self.assertIsNotNone(result.normalized_payload)
        assert result.normalized_payload is not None
        self.assertEqual(len(result.normalized_payload["error_attributions"]), 1)
        self.assertEqual(result.normalized_payload["error_attributions"][0]["anchor_kind"], "missing_relation")
        self.assertIn("not present", "\n".join(result.rejected_patterns[0]["errors"]))

    def test_v3_requirement_quote_must_be_exact_without_format_normalization(self):
        catalog = [
            evidence(
                requirement="After startup, Task A and Task B runconcurrently."
            )
        ]
        result = validate_failure_analysis_payload(
            atomic_payload(
                fork_attribution(
                    requirement_quote="Task A and Task B run concurrently"
                )
            ),
            evidence_catalog=catalog,
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("exact non-empty substring", "\n".join(result.rejected_patterns[0]["errors"]))

    def test_v3_run_rejects_legacy_pattern_schema(self):
        result = validate_failure_analysis_payload(
            {"error_patterns": [{"name": "legacy"}]},
            evidence_catalog=[evidence()],
            required_schema_version="atomic-v1",
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("error_attributions", result.fatal_errors[0])

    def test_same_anchor_multiple_signatures_isolated_without_rejecting_case(self):
        result = validate_failure_analysis_payload(
            atomic_payload(
                fork_attribution(gold_state="present", prediction_state="absent"),
                fork_attribution(gold_state="absent", prediction_state="absent"),
                context_attribution(),
            ),
            evidence_catalog=[evidence()],
        )
        self.assertIsNotNone(result.normalized_payload)
        assert result.normalized_payload is not None
        self.assertEqual(len(result.normalized_payload["error_attributions"]), 1)
        self.assertEqual(result.normalized_payload["error_attributions"][0]["error_anchor"], "After startup")
        self.assertEqual(
            [item["errors"] for item in result.rejected_patterns],
            [["ambiguous_attribution_assignment"], ["ambiguous_attribution_assignment"]],
        )

    def test_non_bijective_matching_forbids_primary_but_keeps_secondary_audit(self):
        primary = fork_attribution()
        secondary = fork_attribution(role="secondary", node_inventory_status="insufficient")
        result = validate_failure_analysis_payload(
            atomic_payload(primary, secondary),
            evidence_catalog=[
                evidence(
                    matching_quality={
                        "status": "non_bijective",
                        "reasons": ["nodes_gold_matches_multiple_predictions"],
                    }
                )
            ],
        )
        self.assertIsNotNone(result.normalized_payload)
        assert result.normalized_payload is not None
        self.assertEqual(result.normalized_payload["error_attributions"][0]["role"], "secondary")
        self.assertEqual(candidate_eligible_attributions(result.normalized_payload, self.taxonomy), [])
        self.assertIn("non-bijective", "\n".join(result.rejected_patterns[0]["errors"]))

    def test_matching_quality_detects_non_bijective_tp_pairs(self):
        record = SimpleNamespace(
            llm_element_metrics=SimpleNamespace(
                status="success",
                matching={
                    "nodes": {
                        "tp": [
                            {"pred": "p1", "gt": "g1"},
                            {"pred": "p2", "gt": "g1"},
                        ]
                    },
                    "relations": {"tp": []},
                },
            )
        )
        quality = matching_quality(record)
        self.assertEqual(quality["status"], "non_bijective")
        self.assertIn("nodes_gold_matches_multiple_predictions", quality["reasons"])

    def test_compiler_error_class_is_python_validated_and_unknown_is_record_only(self):
        compiler_evidence = evidence(
            requirement="Generate the diagram.",
            llm_extra_nodes=[],
            llm_missing_relations=[],
            compile_errors=["No valid @startuml wrapper found", "Unexpected token xyz"],
            plantuml_compiles=False,
        )
        wrapper = {
            "evidence_id": EVIDENCE_ID,
            "role": "primary",
            "requirement_quote": "",
            "error_anchor": "No valid @startuml wrapper found",
            "failure_direction": "syntax_or_format_error",
            "construct_family": "syntax",
            "requirement_trigger": "wrapper_only",
            "gold_state": "valid",
            "prediction_state": "invalid",
            "node_inventory_status": "not_applicable",
            "evidence_basis": "compiler",
            "causal_rationale": "The compiler identifies a missing wrapper.",
        }
        unknown = {
            **wrapper,
            "error_anchor": "Unexpected token xyz",
            "requirement_trigger": "other_compiler_error",
            "causal_rationale": "The compiler message has no narrow supported class.",
        }
        result = validate_failure_analysis_payload(
            atomic_payload(wrapper, unknown),
            evidence_catalog=[compiler_evidence],
        )
        self.assertIsNotNone(result.normalized_payload)
        assert result.normalized_payload is not None
        eligible = candidate_eligible_attributions(result.normalized_payload, self.taxonomy)
        self.assertEqual([item["mechanism_id"] for item in eligible], ["wrapper_syntax_invalid"])

        invalid = validate_failure_analysis_payload(
            atomic_payload({**unknown, "requirement_trigger": "wrapper_only"}),
            evidence_catalog=[compiler_evidence],
        )
        self.assertIsNone(invalid.normalized_payload)
        self.assertIn("other_compiler_error", "\n".join(invalid.rejected_patterns[0]["errors"]))

    def test_v3_context_subtypes_and_candidate_triggers_are_narrow(self):
        candidate_triggers = []
        context_ids = set()
        for mechanism in self.taxonomy["mechanisms"]:
            if mechanism.get("candidate_eligible"):
                trigger = mechanism["match"]["requirement_trigger"]
                self.assertIsInstance(trigger, str)
                candidate_triggers.append(trigger)
            if str(mechanism.get("mechanism_id", "")).endswith("_context_as_activity"):
                context_ids.add(mechanism["mechanism_id"])
        self.assertEqual(
            context_ids,
            {
                "environment_context_as_activity",
                "initial_state_context_as_activity",
                "temporal_context_as_activity",
                "precondition_context_as_activity",
            },
        )
        self.assertNotIn("context_clause", candidate_triggers)

    def test_cluster_grouping_uses_exact_atomic_signature(self):
        base = {
            "mechanism_id": "same-id",
            "candidate_eligible": True,
            "classification": "candidate",
            "evidence_basis": "requirement_and_gold",
            "pattern_names": [],
            "patterns": [],
            "attributions": [],
            "supporting_attribution_ids": [],
            "supporting_evidence_ids": [],
            "supporting_evidence": [],
            "analysis_summary": {},
            "positive_trigger": "positive",
            "negative_boundary": "negative",
        }
        observations = []
        for batch_id, trigger in ((1, "temporal_context"), (2, "environment_context")):
            observations.append(
                {
                    **base,
                    "batch_id": batch_id,
                    "mechanism_signature": {
                        "failure_direction": "activity_over_decomposition",
                        "construct_family": "activity",
                        "requirement_trigger": trigger,
                        "gold_state": "none",
                        "prediction_state": "single",
                        "node_inventory_status": "not_applicable",
                    },
                }
            )
        selected, report = select_epoch_mechanism(observations)
        self.assertIsNotNone(selected)
        self.assertEqual(len(report["eligible_candidates"]), 2)
        self.assertEqual(len(report["parent_clusters"]), 1)
        self.assertEqual(
            len({tuple(item["child_key"]) for item in report["eligible_candidates"]}),
            2,
        )


if __name__ == "__main__":
    unittest.main()
