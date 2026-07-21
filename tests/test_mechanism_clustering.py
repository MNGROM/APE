import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from analysis.failure_analysis import failure_analysis_payload
from analysis.mechanism_clustering import (
    bind_revision_to_mechanism,
    build_mechanism_observations,
    calibration_statistics,
    candidate_eligible_patterns,
    export_legacy_mechanism_evidence,
    load_mechanism_taxonomy,
    make_case_evidence_id,
    sanitize_selected_failure_analysis,
    select_epoch_mechanism,
    validate_failure_analysis_payload,
    validate_selected_revision,
)
from llm_element_metrics import CompilationResult, LLMElementMetrics, PRF
from metrics import EvaluationRecord, SyntaxResult, empty_metric_bundle


PROJECT_DIR = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = PROJECT_DIR / "prompt_workspace" / "mechanism_taxonomy_v1.json"
TAXONOMY_V2_PATH = PROJECT_DIR / "prompt_workspace" / "mechanism_taxonomy_v2.json"


def claim(
    evidence_id: str = "run:i001:b001:a:a-0001",
    *,
    role: str = "primary",
    requirement_quote: str = "Tasks run concurrently",
    error_anchor: str = "A -> B (fork)",
):
    return {
        "evidence_id": evidence_id,
        "role": role,
        "requirement_quote": requirement_quote,
        "error_anchor": error_anchor,
    }


def pattern(**overrides):
    payload = {
        "name": "missing explicit fork",
        "problem": "Explicit concurrency was not represented.",
        "coarse_failure_signals": ["wrong_parallel"],
        "possible_causes": ["The trigger boundary may be unclear."],
        "downstream_guidance": "Revise only if the evidence remains consistent.",
        "failure_direction": "missing_required_parallel",
        "construct_family": "fork",
        "requirement_trigger": "explicit_concurrency",
        "gold_state": "present",
        "prediction_state": "absent",
        "node_inventory_status": "sufficient",
        "evidence_basis": "requirement_and_gold",
        "evidence_claims": [claim()],
    }
    payload.update(overrides)
    return payload


def observation(batch_id: int, dataset: str, case_ids: list[str], *, impact: float = 0.2):
    signature = {
        "failure_direction": "missing_required_parallel",
        "construct_family": "fork",
        "requirement_trigger": "explicit_concurrency",
        "gold_state": "present",
        "prediction_state": "absent",
        "node_inventory_status": "sufficient",
    }
    evidence = [
        {
            "evidence_id": f"run:i001:b{batch_id:03d}:{dataset}:{case_id}",
            "dataset": dataset,
            "case_id": case_id,
            "llm_node_f1": 0.8,
            "llm_relation_f1": 1.0 - impact,
            "plantuml_compiles": True,
        }
        for case_id in case_ids
    ]
    return {
        "batch_id": batch_id,
        "mechanism_id": "explicit_concurrency_not_mapped",
        "mechanism_signature": signature,
        "classification": "candidate",
        "candidate_eligible": True,
        "evidence_basis": "requirement_and_gold",
        "pattern_names": ["missing explicit fork"],
        "patterns": [],
        "supporting_evidence_ids": [item["evidence_id"] for item in evidence],
        "supporting_evidence": evidence,
        "analysis_summary": {},
        "positive_trigger": "Use fork for explicit concurrency.",
        "negative_boundary": "Do not use fork for ordinary lists.",
    }


def activity_observation(batch_id: int, dataset: str, case_ids: list[str]):
    item = observation(batch_id, dataset, case_ids)
    item.update(
        {
            "mechanism_id": "single_action_split_into_unsupported_substeps",
            "mechanism_signature": {
                "failure_direction": "activity_over_decomposition",
                "construct_family": "activity",
                "requirement_trigger": "single_explicit_action",
                "gold_state": "single",
                "prediction_state": "multiple",
                "node_inventory_status": "not_applicable",
            },
            "positive_trigger": "Keep one stated action as one activity.",
            "negative_boundary": "Do not merge distinct explicit actions.",
        }
    )
    return item


def v2_activity_observation(
    batch_id: int,
    dataset: str,
    case_ids: list[str],
    *,
    mechanism_id: str,
    trigger: str,
    gold_state: str,
    prediction_state: str,
):
    item = observation(batch_id, dataset, case_ids)
    item.update(
        {
            "mechanism_id": mechanism_id,
            "mechanism_signature": {
                "failure_direction": "activity_over_decomposition",
                "construct_family": "activity",
                "requirement_trigger": trigger,
                "gold_state": gold_state,
                "prediction_state": prediction_state,
                "node_inventory_status": "not_applicable",
            },
            "positive_trigger": "Keep the selected activity boundary.",
            "negative_boundary": "Preserve explicitly stated behavior.",
        }
    )
    return item


class MechanismClusteringTest(unittest.TestCase):
    def setUp(self) -> None:
        self.taxonomy = load_mechanism_taxonomy(TAXONOMY_PATH)
        self.catalog = [
            {
                "evidence_id": "run:i001:b001:a:a-0001",
                "dataset": "a",
                "case_id": "a-0001",
                "requirement": "Tasks run concurrently. One action is stated.",
                "llm_missing_nodes": ["Missing action"],
                "llm_extra_nodes": ["Extra action"],
                "llm_missing_relations": ["A -> B (fork)"],
                "llm_extra_relations": ["A -> B (sequential)"],
                "plantuml_compiles": True,
            }
        ]

    def test_evidence_id_is_stable_and_source_scoped(self) -> None:
        evidence_id = make_case_evidence_id(
            generation_run="2026 run",
            iteration=2,
            batch_id=3,
            dataset="fsd",
            case_id="fsd-0012",
        )
        self.assertEqual(evidence_id, "2026_run:i002:b003:fsd:fsd-0012")

    def test_v1_remains_loadable_and_v2_splits_activity_over_decomposition(self) -> None:
        self.assertEqual(
            hashlib.sha256(TAXONOMY_PATH.read_bytes()).hexdigest(),
            "ad09f86bc4332463a2345eda29d8f142d55c4df346b7919c368c337eb6b8110f",
        )
        self.assertEqual(self.taxonomy["version"], "v1")
        taxonomy_v2 = load_mechanism_taxonomy(TAXONOMY_V2_PATH)
        self.assertEqual(taxonomy_v2["version"], "v2")

        context = pattern(
            name="context clause as activity",
            failure_direction="activity_over_decomposition",
            construct_family="activity",
            requirement_trigger="context_clause",
            gold_state="none",
            prediction_state="single",
            node_inventory_status="not_applicable",
            evidence_basis="requirement_and_gold",
            evidence_claims=[
                claim(requirement_quote="One action is stated.", error_anchor="Extra action")
            ],
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [context]},
            evidence_catalog=self.catalog,
        )
        eligible = candidate_eligible_patterns(result.normalized_payload, taxonomy_v2)
        self.assertEqual(eligible[0]["mechanism_id"], "context_clause_as_activity")

        context["evidence_basis"] = "requirement_only"
        result = validate_failure_analysis_payload(
            {"error_patterns": [context]},
            evidence_catalog=self.catalog,
        )
        self.assertEqual(candidate_eligible_patterns(result.normalized_payload, taxonomy_v2), [])

        legacy = pattern(
            name="legacy broad activity pattern",
            failure_direction="activity_over_decomposition",
            construct_family="activity",
            requirement_trigger="single_explicit_action",
            gold_state="single",
            prediction_state="multiple",
            node_inventory_status="not_applicable",
            evidence_basis="requirement_and_gold",
            evidence_claims=[
                claim(requirement_quote="One action is stated.", error_anchor="Extra action")
            ],
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [legacy]},
            evidence_catalog=self.catalog,
        )
        self.assertEqual(candidate_eligible_patterns(result.normalized_payload, taxonomy_v2), [])
        observations = build_mechanism_observations(
            result.normalized_payload,
            taxonomy_v2,
            batch_id=1,
            analysis_summary={},
        )
        self.assertEqual(observations[0]["classification"], "record_only")

        substeps = pattern(
            name="unstated implementation substeps",
            failure_direction="activity_over_decomposition",
            construct_family="activity",
            requirement_trigger="unstated_implementation_substeps",
            gold_state="single",
            prediction_state="multiple",
            node_inventory_status="not_applicable",
            evidence_basis="requirement_only",
            evidence_claims=[
                claim(requirement_quote="One action is stated.", error_anchor="Extra action")
            ],
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [substeps]},
            evidence_catalog=self.catalog,
        )
        eligible = candidate_eligible_patterns(result.normalized_payload, taxonomy_v2)
        self.assertEqual(eligible[0]["mechanism_id"], "single_action_split_into_unsupported_substeps")

    def test_selected_failure_analysis_removes_uncounted_claims_and_free_text(self) -> None:
        selected = {
            "supporting_evidence_ids": ["e1"],
            "supporting_evidence": [
                {"evidence_id": "e1", "dataset": "a", "case_id": "a-1"},
                {"evidence_id": "e2", "dataset": "b", "case_id": "b-1"},
            ],
            "patterns": [
                {
                    "name": "context pattern",
                    "failure_direction": "activity_over_decomposition",
                    "construct_family": "activity",
                    "requirement_trigger": "context_clause",
                    "gold_state": "none",
                    "prediction_state": "single",
                    "node_inventory_status": "not_applicable",
                    "evidence_basis": "requirement_and_gold",
                    "evidence_claims": [
                        {
                            "evidence_id": "e1",
                            "role": "primary",
                            "requirement_quote": "After startup",
                            "error_anchor": "startup",
                        },
                        {
                            "evidence_id": "e2",
                            "role": "primary",
                            "requirement_quote": "based on performance",
                            "error_anchor": "performance",
                        },
                    ],
                    "problem": "This free text mentions excluded rationale evidence.",
                    "possible_causes": ["Excluded rationale phrase"],
                    "downstream_guidance": "Add a broad rule.",
                }
            ],
        }
        sanitized = sanitize_selected_failure_analysis(selected)
        self.assertEqual(
            sanitized["error_patterns"][0]["evidence_claims"][0]["evidence_id"],
            "e1",
        )
        self.assertEqual([item["evidence_id"] for item in sanitized["evidence_catalog"]], ["e1"])
        self.assertNotIn("problem", sanitized["error_patterns"][0])
        self.assertNotIn("possible_causes", sanitized["error_patterns"][0])
        self.assertNotIn("downstream_guidance", sanitized["error_patterns"][0])

        selected["supporting_evidence_ids"] = ["missing"]
        sanitized = sanitize_selected_failure_analysis(selected)
        self.assertEqual(sanitized["error_patterns"], [])

    def test_latest_run_regression_fixture_keeps_context_and_substeps_separate(self) -> None:
        observations = [
            v2_activity_observation(
                1,
                "rac",
                ["rac-0014", "rac-0017"],
                mechanism_id="context_clause_as_activity",
                trigger="context_clause",
                gold_state="none",
                prediction_state="single",
            ),
            v2_activity_observation(
                2,
                "lmc",
                ["lmc-0009"],
                mechanism_id="context_clause_as_activity",
                trigger="context_clause",
                gold_state="none",
                prediction_state="single",
            ),
            v2_activity_observation(
                3,
                "lmc",
                ["lmc-0043", "lmc-0050"],
                mechanism_id="single_action_split_into_unsupported_substeps",
                trigger="unstated_implementation_substeps",
                gold_state="single",
                prediction_state="multiple",
            ),
        ]
        selected, report = select_epoch_mechanism(observations)
        self.assertEqual(selected["mechanism_id"], "context_clause_as_activity")
        self.assertEqual(selected["supporting_batch_count"], 2)
        self.assertEqual(selected["supporting_case_count"], 3)
        self.assertEqual(len(report["eligible_candidates"]), 2)
        self.assertEqual(len(report["parent_clusters"]), 2)

    def test_failure_analysis_payload_uses_one_case_scoped_evidence_source(self) -> None:
        llm_metrics = LLMElementMetrics(
            enabled=True,
            status="success",
            node_metrics=PRF(precision=0.5, recall=0.5, f1=0.5),
            relation_metrics=PRF(precision=0.5, recall=0.5, f1=0.5),
            gt_elements={},
            pred_elements={},
            matching={
                "nodes": {"fn": ["Missing action"], "fp": ["Extra action"]},
                "relations": {"fn": [], "fp": []},
            },
            counts={"node_tp": 1, "node_fp": 1, "node_fn": 1},
        )
        record = EvaluationRecord(
            dataset="a",
            case_id="a-0001",
            input_requirement="Tasks run concurrently.",
            gold_plantuml="@startuml\nstart\nstop\n@enduml",
            generated_plantuml="@startuml\nstart\nstop\n@enduml",
            syntax=SyntaxResult(True, []),
            node_metrics=empty_metric_bundle(),
            relation_metrics=empty_metric_bundle(),
            plantuml_compilation=CompilationResult(True, []),
            llm_element_metrics=llm_metrics,
            failure_types=["missing_activity", "extra_activity"],
        )
        payload = failure_analysis_payload(
            [record],
            {"count": 1.0},
            generation_run="run",
            iteration=1,
            batch_id=2,
        )
        self.assertNotIn("requirements", payload)
        self.assertNotIn("predictions", payload)
        self.assertNotIn("ground_truths", payload)
        self.assertNotIn("failure_types", payload)
        self.assertIn("failure_type_guide", payload)
        self.assertEqual(payload["case_evidence"][0]["requirement"], record.input_requirement)
        self.assertEqual(payload["case_evidence"][0]["llm_extra_nodes"], ["Extra action"])

    def test_failure_analysis_schema_rejects_fabricated_evidence_id(self) -> None:
        payload = {"error_patterns": [pattern(evidence_claims=[claim("fabricated")])]}
        result = validate_failure_analysis_payload(payload, evidence_catalog=self.catalog)
        self.assertIsNone(result.normalized_payload)
        self.assertTrue(any("unknown evidence ID" in error for item in result.rejected_patterns for error in item["errors"]))

    def test_failure_analysis_schema_rejects_legacy_supporting_ids(self) -> None:
        legacy = pattern()
        legacy["supporting_evidence_ids"] = ["run:i001:b001:a:a-0001"]
        result = validate_failure_analysis_payload(
            {"error_patterns": [legacy]}, evidence_catalog=self.catalog
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("must use evidence_claims", "\n".join(result.rejected_patterns[0]["errors"]))

    def test_failure_analysis_claim_requires_exact_quote_and_anchor(self) -> None:
        invalid = pattern(
            evidence_claims=[
                claim(requirement_quote="Concurrent work happens", error_anchor="invented edge")
            ]
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [invalid]}, evidence_catalog=self.catalog
        )
        self.assertIsNone(result.normalized_payload)
        errors = "\n".join(result.rejected_patterns[0]["errors"])
        self.assertIn("exact non-empty requirement substring", errors)
        self.assertIn("not present in the case evaluator evidence", errors)

    def test_failure_analysis_claim_allows_deterministic_format_normalization(self) -> None:
        catalog = [
            {
                **self.catalog[0],
                "requirement": "Enter credentials, select authentication, andclick Login.",
            }
        ]
        formatted = pattern(
            evidence_claims=[
                claim(
                    requirement_quote="Enter credentials, select authentication, and click Login."
                )
            ]
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [formatted]}, evidence_catalog=catalog
        )
        self.assertIsNotNone(result.normalized_payload)

    def test_failure_analysis_claim_rejects_non_local_requirement_quote(self) -> None:
        long_requirement = "Tasks run concurrently. " + "x" * 320
        catalog = [{**self.catalog[0], "requirement": long_requirement}]
        invalid = pattern(
            evidence_claims=[claim(requirement_quote=long_requirement)]
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [invalid]}, evidence_catalog=catalog
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("exceeds 300", "\n".join(result.rejected_patterns[0]["errors"]))

    def test_failure_analysis_claim_anchor_must_match_direction(self) -> None:
        invalid = pattern(
            failure_direction="activity_over_decomposition",
            construct_family="activity",
            requirement_trigger="single_explicit_action",
            gold_state="single",
            prediction_state="multiple",
            node_inventory_status="not_applicable",
            evidence_claims=[claim(error_anchor="A -> B (fork)")],
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [invalid]}, evidence_catalog=self.catalog
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("incompatible", "\n".join(result.rejected_patterns[0]["errors"]))

    def test_secondary_claim_may_anchor_a_downstream_error(self) -> None:
        item = pattern(
            failure_direction="activity_over_decomposition",
            construct_family="activity",
            requirement_trigger="single_explicit_action",
            gold_state="single",
            prediction_state="multiple",
            node_inventory_status="not_applicable",
            evidence_claims=[claim(role="secondary", error_anchor="A -> B (fork)")],
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [item]}, evidence_catalog=self.catalog
        )
        self.assertIsNotNone(result.normalized_payload)

    def test_failure_analysis_schema_rejects_invalid_family_state(self) -> None:
        payload = {"error_patterns": [pattern(gold_state="multiple")]}
        result = validate_failure_analysis_payload(payload, evidence_catalog=self.catalog)
        self.assertIsNone(result.normalized_payload)
        self.assertTrue(any("gold_state is invalid" in error for item in result.rejected_patterns for error in item["errors"]))

    def test_failure_analysis_isolates_invalid_pattern(self) -> None:
        payload = {
            "error_patterns": [
                pattern(),
                pattern(name="fabricated", evidence_claims=[claim("fabricated")]),
            ]
        }
        result = validate_failure_analysis_payload(payload, evidence_catalog=self.catalog)
        self.assertIsNotNone(result.normalized_payload)
        assert result.normalized_payload is not None
        self.assertEqual(len(result.normalized_payload["error_patterns"]), 1)
        self.assertEqual(len(result.rejected_patterns), 1)

    def test_invalid_claim_rejects_its_whole_signature_pattern(self) -> None:
        item = pattern(
            evidence_claims=[
                claim(),
                claim("fabricated", requirement_quote="Tasks run concurrently"),
            ]
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [item]}, evidence_catalog=self.catalog
        )
        self.assertIsNone(result.normalized_payload)
        self.assertEqual(len(result.rejected_patterns), 1)
        self.assertIn(
            "unknown evidence ID",
            "\n".join(result.rejected_patterns[0]["errors"]),
        )

    def test_activity_inventory_status_must_be_not_applicable(self) -> None:
        activity = pattern(
            failure_direction="activity_over_decomposition",
            construct_family="activity",
            requirement_trigger="single_explicit_action",
            gold_state="single",
            prediction_state="multiple",
            node_inventory_status="insufficient",
            evidence_claims=[claim(requirement_quote="One action", error_anchor="Extra action")],
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [activity]}, evidence_catalog=self.catalog
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("not_applicable", "\n".join(result.rejected_patterns[0]["errors"]))

    def test_compiler_evidence_requires_a_confirmed_compile_failure(self) -> None:
        syntax_pattern = pattern(
            failure_direction="syntax_or_format_error",
            construct_family="syntax",
            requirement_trigger="compiler_confirmed",
            gold_state="valid",
            prediction_state="invalid",
            node_inventory_status="not_applicable",
            evidence_basis="compiler",
            evidence_claims=[claim(requirement_quote="", error_anchor="compile_failed")],
        )
        catalog = [dict(self.catalog[0], plantuml_compiles=True)]
        result = validate_failure_analysis_payload(
            {"error_patterns": [syntax_pattern]}, evidence_catalog=catalog
        )
        self.assertIsNone(result.normalized_payload)
        self.assertTrue(any("case that compiled" in error for item in result.rejected_patterns for error in item["errors"]))

    def test_non_compiler_syntax_evidence_uses_local_syntax_status(self) -> None:
        syntax_pattern = pattern(
            failure_direction="syntax_or_format_error",
            construct_family="syntax",
            requirement_trigger="wrapper_only",
            gold_state="valid",
            prediction_state="invalid",
            node_inventory_status="not_applicable",
            evidence_basis="requirement_and_gold",
            evidence_claims=[claim(error_anchor="syntax_failed")],
        )
        catalog = [dict(self.catalog[0], syntax_passed=False)]
        result = validate_failure_analysis_payload(
            {"error_patterns": [syntax_pattern]}, evidence_catalog=catalog
        )
        self.assertIsNotNone(result.normalized_payload)
        assert result.normalized_payload is not None
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertEqual(observations[0]["classification"], "record_only")

    def test_taxonomy_separates_candidate_and_dataset_convention(self) -> None:
        result = validate_failure_analysis_payload(
            {"error_patterns": [pattern()]}, evidence_catalog=self.catalog
        )
        self.assertFalse(result.fatal_errors)
        valid = result.normalized_payload
        assert valid is not None
        eligible = candidate_eligible_patterns(valid, self.taxonomy)
        self.assertEqual(eligible[0]["mechanism_id"], "explicit_concurrency_not_mapped")

        convention = pattern(
            requirement_trigger="ordinary_enumeration",
            evidence_basis="gold_only",
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [convention]}, evidence_catalog=self.catalog
        )
        valid = result.normalized_payload
        assert valid is not None
        self.assertEqual(candidate_eligible_patterns(valid, self.taxonomy), [])

    def test_requirement_only_evidence_is_candidate_eligible(self) -> None:
        result = validate_failure_analysis_payload(
            {"error_patterns": [pattern(evidence_basis="requirement_only")]},
            evidence_catalog=self.catalog,
        )
        assert result.normalized_payload is not None
        eligible = candidate_eligible_patterns(result.normalized_payload, self.taxonomy)
        self.assertEqual(eligible[0]["mechanism_id"], "explicit_concurrency_not_mapped")

    def test_secondary_evidence_does_not_create_candidate_support(self) -> None:
        secondary = pattern(evidence_claims=[claim(role="secondary")])
        result = validate_failure_analysis_payload(
            {"error_patterns": [secondary]}, evidence_catalog=self.catalog
        )
        assert result.normalized_payload is not None
        self.assertEqual(candidate_eligible_patterns(result.normalized_payload, self.taxonomy), [])
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertEqual(observations[0]["classification"], "record_only")
        self.assertIn("no_primary_evidence", observations[0]["candidate_exclusion_reasons"])

    def test_legacy_evidence_strength_does_not_preempt_python_aggregation(self) -> None:
        for legacy_strength in (None, "isolated", "repeated_mixed"):
            item = pattern()
            if legacy_strength is not None:
                item["evidence_strength"] = legacy_strength
            result = validate_failure_analysis_payload(
                {"error_patterns": [item]}, evidence_catalog=self.catalog
            )
            assert result.normalized_payload is not None
            eligible = candidate_eligible_patterns(result.normalized_payload, self.taxonomy)
            self.assertEqual(len(eligible), 1)
            observations = build_mechanism_observations(
                result.normalized_payload,
                self.taxonomy,
                batch_id=1,
                analysis_summary={},
            )
            self.assertTrue(observations[0]["candidate_eligible"])
            selected, report = select_epoch_mechanism(observations)
        self.assertIsNotNone(selected)
        self.assertEqual(report["selected_mechanism_id"], "explicit_concurrency_not_mapped")

    def test_explicit_concurrency_requires_requirement_grounding(self) -> None:
        catalog = [
            {
                **self.catalog[0],
                "requirement": "Show percentage changes and lists of changed pages.",
            }
        ]
        ungrounded = pattern(
            evidence_claims=[
                claim(requirement_quote="percentage changes and lists of changed pages")
            ]
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [ungrounded]}, evidence_catalog=catalog
        )
        assert result.normalized_payload is not None
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertEqual(observations[0]["classification"], "record_only")
        self.assertIn(
            "requirement_trigger_not_grounded",
            observations[0]["candidate_exclusion_reasons"],
        )

    def test_only_primary_claims_count_as_candidate_support(self) -> None:
        second = {
            **self.catalog[0],
            "evidence_id": "run:i001:b001:b:b-0002",
            "dataset": "b",
            "case_id": "b-0002",
        }
        item = pattern(
            evidence_claims=[
                claim(),
                claim(second["evidence_id"], role="secondary"),
            ]
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [item]}, evidence_catalog=[self.catalog[0], second]
        )
        assert result.normalized_payload is not None
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertTrue(observations[0]["candidate_eligible"])
        self.assertEqual(
            observations[0]["supporting_evidence_ids"],
            ["run:i001:b001:a:a-0001"],
        )

    def test_one_case_cannot_be_primary_for_two_candidate_signatures(self) -> None:
        catalog = [
            {
                **self.catalog[0],
                "requirement": "Tasks run concurrently until processing is complete.",
            }
        ]
        concurrency = pattern(
            evidence_claims=[
                claim(requirement_quote="Tasks run concurrently until processing is complete")
            ]
        )
        iteration = pattern(
            name="missing explicit loop",
            failure_direction="missing_required_loop",
            construct_family="loop",
            requirement_trigger="explicit_iteration_with_exit",
            gold_state="present",
            prediction_state="absent",
            evidence_claims=[
                claim(requirement_quote="Tasks run concurrently until processing is complete")
            ],
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [concurrency, iteration]}, evidence_catalog=catalog
        )
        assert result.normalized_payload is not None
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertTrue(all(not item["candidate_eligible"] for item in observations))
        self.assertTrue(
            all(
                "ambiguous_primary_assignment" in item["candidate_exclusion_reasons"]
                for item in observations
            )
        )

    def test_observation_inventory_records_non_candidate_branch(self) -> None:
        branch = pattern(
            failure_direction="condition_or_branch_error",
            construct_family="branch",
            requirement_trigger="exclusive_values",
            gold_state="switch",
            prediction_state="if",
        )
        result = validate_failure_analysis_payload(
            {"error_patterns": [branch]}, evidence_catalog=self.catalog
        )
        assert result.normalized_payload is not None
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertEqual(observations[0]["classification"], "record_only")
        self.assertFalse(observations[0]["candidate_eligible"])

    def test_selected_revision_must_reference_matching_batch_evidence(self) -> None:
        result = validate_failure_analysis_payload(
            {"error_patterns": [pattern()]}, evidence_catalog=self.catalog
        )
        valid = result.normalized_payload
        assert valid is not None
        payload = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "selected_mechanism_signature": pattern(),
            "supporting_evidence_ids": ["fabricated"],
        }
        normalized, errors = validate_selected_revision(
            payload, failure_analysis=valid, taxonomy=self.taxonomy
        )
        self.assertIsNone(normalized)
        self.assertTrue(any("not evidence" in error for error in errors))

    def test_epoch_selection_uses_datasets_cases_then_batches(self) -> None:
        inputs = [
            observation(1, "a", ["a-0001", "a-0002"]),
            observation(2, "b", ["b-0001"]),
        ]
        selected, report = select_epoch_mechanism(inputs)
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["mechanism_id"], "explicit_concurrency_not_mapped")
        self.assertEqual(selected["supporting_dataset_count"], 2)
        self.assertEqual(selected["supporting_case_count"], 3)
        self.assertEqual(report["selected_mechanism_id"], "explicit_concurrency_not_mapped")

    def test_epoch_selection_deduplicates_batch_and_case_support(self) -> None:
        inputs = [
            observation(1, "a", ["a-0001", "a-0002"]),
            observation(1, "a", ["a-0002"]),
            observation(2, "b", ["b-0001"]),
        ]
        selected, _ = select_epoch_mechanism(inputs)
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["supporting_batch_count"], 2)
        self.assertEqual(selected["supporting_case_count"], 3)
        self.assertEqual(len(selected["supporting_batch_observations"]), 2)

    def test_epoch_selection_rejects_insufficient_cross_dataset_support(self) -> None:
        inputs = [
            observation(1, "a", ["a-0001", "a-0002"]),
            observation(2, "a", ["a-0003"]),
        ]
        selected, report = select_epoch_mechanism(inputs)
        self.assertIsNotNone(selected)
        self.assertEqual(selected["supporting_dataset_count"], 1)
        self.assertEqual(report["selected_mechanism_id"], "explicit_concurrency_not_mapped")

    def test_epoch_selection_replays_single_action_cluster_before_editing(self) -> None:
        observations = [
            activity_observation(3, "lmc", ["lmc-0050", "lmc-0043"]),
            activity_observation(4, "bp", ["bp-0017"]),
        ]
        selected, report = select_epoch_mechanism(observations)
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected["mechanism_id"], "single_action_split_into_unsupported_substeps")
        self.assertEqual(selected["supporting_batch_count"], 2)
        self.assertEqual(report["eligible_candidates"][0]["supporting_case_count"], 3)

    def test_epoch_selection_counts_opposite_batches_and_is_order_independent(self) -> None:
        inputs = [
            observation(1, "a", ["a-1", "a-2"]),
            observation(2, "b", ["b-1"]),
        ]
        opposite = observation(3, "c", ["c-1"])
        opposite.update(
            {
                "mechanism_id": None,
                "candidate_eligible": False,
                "classification": "record_only",
                "mechanism_signature": {
                    **inputs[0]["mechanism_signature"],
                    "gold_state": "absent",
                    "prediction_state": "present",
                },
                "attributions": [{"attribution_id": "opposite", "role": "primary"}],
            }
        )
        selected, _ = select_epoch_mechanism([opposite, *reversed(inputs)])
        self.assertIsNone(selected)

    def test_python_binds_frozen_revision_metadata(self) -> None:
        selected = observation(1, "a", ["a-1"])
        payload = {
            "revision_plan": [
                {
                    "section": "knowledge",
                    "operation": "append_new",
                    "intent": "Clarify concurrency.",
                    "change_instruction": "Add a narrow fork rule.",
                }
            ]
        }
        bound, errors = bind_revision_to_mechanism(payload, selected_mechanism=selected)
        self.assertFalse(errors)
        assert bound is not None
        self.assertEqual(bound["mechanism_id"], selected["mechanism_id"])
        self.assertEqual(bound["revision_plan"][0]["negative_boundary"], selected["negative_boundary"])

    def test_python_rejects_model_override_of_mechanism_metadata(self) -> None:
        selected = observation(1, "a", ["a-1"])
        payload = {
            "mechanism_id": "unsupported_fork",
            "revision_plan": [
                {
                    "section": "knowledge",
                    "operation": "append_new",
                    "intent": "Change another mechanism.",
                    "change_instruction": "Add another rule.",
                }
            ],
        }
        bound, errors = bind_revision_to_mechanism(payload, selected_mechanism=selected)
        self.assertIsNone(bound)
        self.assertIn("mechanism_id", "\n".join(errors))

    def test_calibration_threshold_uses_sampling_error_and_resolution(self) -> None:
        result = calibration_statistics([0.4, 0.5, 0.6, 0.5, 0.5], validation_repeats=3)
        self.assertGreater(result["suggested_min_delta"], 0.0)
        compile_result = calibration_statistics(
            [1.0, 1.0, 1.0, 1.0, 1.0], validation_repeats=3, metric_resolution=1 / 30
        )
        self.assertAlmostEqual(compile_result["suggested_min_delta"], 1 / 30)

    def test_legacy_export_maps_valid_indexes_and_reports_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source-run"
            agents = source / "iteration_001" / "train_batches" / "batch_001" / "agents"
            agents.mkdir(parents=True)
            input_payload = {
                "case_evidence": [
                    {
                        "dataset": "a",
                        "case_id": "a-0001",
                        "requirement": "R",
                        "prediction": "P",
                        "ground_truth": "G",
                    }
                ]
            }
            (agents / "failure_analysis.input.json").write_text(json.dumps(input_payload), encoding="utf-8")
            output_payload = {
                "error_patterns": [
                    {
                        "name": "p",
                        "failure_direction": "missing_required_parallel",
                        "evidence_strength": "repeated_consistent",
                        "problem": "problem",
                        "supporting_cases": [1, 2],
                    }
                ]
            }
            (agents / "failure_analysis.output.json").write_text(
                "```json\n" + json.dumps(output_payload) + "\n```", encoding="utf-8"
            )
            audit_dir, summary = export_legacy_mechanism_evidence(source, root / "runs")
            self.assertEqual(summary["valid_reference_count"], 1)
            self.assertEqual(summary["invalid_reference_count"], 1)
            self.assertTrue((audit_dir / "mechanism_audit.csv").exists())


if __name__ == "__main__":
    unittest.main()
