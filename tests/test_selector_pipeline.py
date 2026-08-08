import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from analysis.error_selector import (
    _selector_input,
    build_failure_analysis_input,
    select_error_group,
    selected_group_evidence_family,
    selected_group_required_metrics,
    validate_failure_errors,
    validate_selected_group_eligibility,
    validate_selector_output,
)
from analysis.failure_analysis import analyze_failures
from analysis.candidate_registry import record_group_attempt
from analysis.selector_agents import (
    _validate_prompt_gap_localization,
    _shared_repair_contract_errors,
    build_rewriter_plan,
    localize_selector_group,
    propose_selector_edit,
)
from analysis.prompt_rewriter import rewrite_prompt, rule_sentence_count
from llm_element_metrics import CompilationResult, LLMElementMetrics, PRF
from metrics import EvaluationRecord, SyntaxResult, empty_metric_bundle
from prompt_ops import apply_prompt_revision_fragment
from ape_datasets.lato import Case
from run import (
    EpochBatchResult,
    build_parser,
    exact_already_covered_recurrence,
    filter_candidate_groups_by_attempt_history,
    resolve_pipeline_defaults,
    run_training_iterations,
    selector_application_decision,
)


PROJECT_DIR = Path(__file__).resolve().parents[1]


def record(
    case_id: str,
    *,
    requirement: str = "The user opens the database.",
    missing_nodes=None,
    extra_nodes=None,
    missing_relations=None,
    extra_relations=None,
    compile_errors=None,
    syntax_errors=None,
    matching=None,
):
    llm_metrics = LLMElementMetrics(
        enabled=True,
        status="success",
        node_metrics=PRF(0.5, 0.5, 0.5),
        relation_metrics=PRF(1.0, 1.0, 1.0),
        gt_elements={},
        pred_elements={},
        matching=matching
        or {
            "nodes": {
                "tp": [],
                "fn": list(missing_nodes or []),
                "fp": list(extra_nodes or []),
            },
            "relations": {
                "tp": [],
                "fn": list(missing_relations or []),
                "fp": list(extra_relations or []),
            },
        },
        counts={},
    )
    compile_errors = list(compile_errors or [])
    return EvaluationRecord(
        dataset="data",
        case_id=case_id,
        input_requirement=requirement,
        gold_plantuml="@startuml\n:Open database;\n@enduml",
        generated_plantuml="@startuml\nstart\n@enduml",
        syntax=SyntaxResult(not syntax_errors, list(syntax_errors or [])),
        node_metrics=empty_metric_bundle(),
        relation_metrics=empty_metric_bundle(),
        plantuml_compilation=CompilationResult(not compile_errors, compile_errors),
        llm_element_metrics=llm_metrics,
        failure_types=["missing_activity"],
    )


class SelectorPipelineTest(unittest.TestCase):
    def test_finding_input_is_stable_numeric_and_balances_semantic_types(self):
        relation = {"from": "A", "to": "B", "type": "sequential"}
        payload = build_failure_analysis_input(
            [
                record(
                    "c1",
                    missing_nodes=["Open database", "Select file"],
                    extra_nodes=["Home page"],
                    missing_relations=[relation],
                    extra_relations=[{"from": "X", "to": "Y", "type": "conditional"}],
                ),
            ],
            generation_run="run",
            iteration=1,
            batch_id=2,
            finding_budget=4,
        )

        self.assertEqual(payload["schema_version"], "failure-analysis-input-v2")
        findings = payload["cases"][0]["findings"]
        self.assertEqual([item["finding_id"] for item in findings], [1001, 1002, 1003, 1004])
        self.assertEqual(
            {item["anchor_kind"] for item in findings},
            {"missing_node", "extra_node", "missing_relation", "extra_relation"},
        )
        self.assertTrue(all(item["finding_key"].startswith("finding_key_") for item in findings))
        repeated = build_failure_analysis_input(
            [
                record(
                    "c1",
                    missing_nodes=["Open database", "Select file"],
                    extra_nodes=["Home page"],
                    missing_relations=[relation],
                    extra_relations=[{"from": "X", "to": "Y", "type": "conditional"}],
                ),
            ],
            generation_run="run",
            iteration=1,
            batch_id=2,
            finding_budget=4,
        )
        self.assertEqual(payload, repeated)
        next_epoch = build_failure_analysis_input(
            [
                record(
                    "c1",
                    missing_nodes=["Open database", "Select file"],
                    extra_nodes=["Home page"],
                    missing_relations=[relation],
                    extra_relations=[{"from": "X", "to": "Y", "type": "conditional"}],
                ),
            ],
            generation_run="run",
            iteration=2,
            batch_id=1,
            finding_budget=4,
        )
        self.assertEqual(
            {item["finding_key"] for item in findings},
            {
                item["finding_key"]
                for item in next_epoch["cases"][0]["findings"]
            },
        )

    def test_failure_error_validation_enriches_exact_finding(self):
        input_payload = build_failure_analysis_input(
            [record("c1", missing_nodes=["Open database"])],
            generation_run="run",
            iteration=1,
            batch_id=1,
        )
        finding_id = input_payload["cases"][0]["findings"][0]["finding_id"]
        result = validate_failure_errors(
            {
                "schema_version": "failure-errors-v2",
                "errors": [
                    {
                        "finding_id": finding_id,
                        "status": "actionable",
                        "primary_finding_id": None,
                        "requirement_quote": "The user opens the database",
                        "error_summary": "An explicit action is missing.",
                        "causal_rationale": "The exact requirement states the omitted action.",
                    }
                ],
            },
            input_payload=input_payload,
        )

        self.assertIsNotNone(result.normalized_payload)
        error = result.normalized_payload["errors"][0]
        self.assertEqual(error["anchor_kind"], "missing_node")
        self.assertEqual(error["case_id"], "c1")
        self.assertEqual(error["matching_quality"], "bijective")

    def test_failure_analysis_hides_internal_key_from_agent(self):
        class Client:
            payload = None

            def chat(self, messages, **kwargs):
                self.payload = json.loads(messages[1]["content"])
                finding_id = self.payload["cases"][0]["findings"][0]["finding_id"]
                return json.dumps(
                    {
                        "schema_version": "failure-errors-v2",
                        "errors": [
                            {
                                "finding_id": finding_id,
                                "status": "actionable",
                                "primary_finding_id": None,
                                "requirement_quote": "The user opens the database",
                                "error_summary": "An explicit action is missing.",
                                "causal_rationale": "The requirement states the action.",
                            }
                        ],
                    }
                )

        client = Client()
        args = SimpleNamespace(
            failure_analysis_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "failure_analysis_selector_v2.md"
            ),
            analysis_temperature=0.0,
            analysis_max_tokens=1024,
            analysis_thinking="disabled",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = analyze_failures(
                current_prompt="Prompt",
                records=[record("c1", missing_nodes=["Open database"])],
                summary={},
                args=args,
                llm_client=client,
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                raw_output_path=root / "raw.txt",
                rejected_patterns_path=root / "rejected.json",
                state_dir=root,
                iteration=1,
                batch_id=1,
                generation_run="run",
            )

        self.assertIsNotNone(result.normalized_payload)
        self.assertNotIn("finding_key", client.payload["cases"][0]["findings"][0])
        self.assertTrue(
            result.normalized_payload["errors"][0]["finding_key"].startswith(
                "finding_key_"
            )
        )

    def test_non_bijective_finding_cannot_be_actionable(self):
        non_bijective = {
            "nodes": {
                "tp": [
                    {"pred": "Open", "gt": "Other database"},
                    {"pred": "Open", "gt": "Open file"},
                ],
                "fn": ["Open database"],
                "fp": [],
            },
            "relations": {"tp": [], "fn": [], "fp": []},
        }
        input_payload = build_failure_analysis_input(
            [record("c1", missing_nodes=["Open database"], matching=non_bijective)],
            generation_run="run",
            iteration=1,
            batch_id=1,
        )
        finding_id = input_payload["cases"][0]["findings"][0]["finding_id"]
        result = validate_failure_errors(
            {
                "schema_version": "failure-errors-v2",
                "errors": [
                    {
                        "finding_id": finding_id,
                        "status": "actionable",
                        "primary_finding_id": None,
                        "requirement_quote": "The user opens the database",
                        "error_summary": "Missing action.",
                        "causal_rationale": "The action appears missing.",
                    }
                ],
            },
            input_payload=input_payload,
        )
        self.assertIsNone(result.normalized_payload)
        self.assertTrue(
            any(
                item.get("finding_id") == finding_id
                and "non-bijective" in " ".join(item.get("errors", []))
                for item in result.rejected_patterns
            )
        )

    def test_generic_compiler_is_recorded_without_consuming_llm_budget(self):
        compiler_input = build_failure_analysis_input(
            [record("c2", compile_errors=["Some diagram description contains errors"])],
            generation_run="run",
            iteration=1,
            batch_id=1,
            finding_budget=1,
        )
        self.assertEqual(compiler_input["cases"], [])
        self.assertEqual(len(compiler_input["_automatic_errors"]), 1)
        self.assertEqual(compiler_input["_automatic_errors"][0]["status"], "uncertain")

    def test_exact_error_compiler_token_is_generic(self):
        compiler_input = build_failure_analysis_input(
            [record("c2", compile_errors=["ERROR"])],
            generation_run="run",
            iteration=1,
            batch_id=1,
            finding_budget=1,
        )
        self.assertEqual(compiler_input["cases"], [])
        self.assertEqual(len(compiler_input["_automatic_errors"]), 1)
        self.assertEqual(compiler_input["_automatic_errors"][0]["status"], "uncertain")

    def test_selected_group_rejects_generic_diagnostic_and_mixed_family(self):
        generic = {
            "finding_id": 1,
            "status": "actionable",
            "anchor_kind": "compile_error",
            "error_anchor": "ERROR",
            "matching_quality": "bijective",
        }
        semantic = {
            "finding_id": 2,
            "status": "actionable",
            "anchor_kind": "missing_node",
            "error_anchor": "Open database",
            "matching_quality": "bijective",
        }
        errors = validate_selected_group_eligibility(
            {"members": [generic, semantic]}
        )
        self.assertTrue(any("generic" in item for item in errors))
        self.assertTrue(any("mixes semantic" in item for item in errors))

    def test_selected_group_evidence_family_is_derived_from_anchor_kind(self):
        def group(*anchor_kinds):
            return {
                "members": [
                    {
                        "finding_id": index,
                        "status": "actionable",
                        "anchor_kind": anchor_kind,
                        "error_anchor": f"specific {anchor_kind} evidence",
                        "matching_quality": "bijective",
                    }
                    for index, anchor_kind in enumerate(anchor_kinds, start=1)
                ]
            }

        self.assertEqual(
            selected_group_evidence_family(group("missing_node", "extra_relation")),
            "semantic",
        )
        self.assertEqual(
            selected_group_required_metrics(
                group("missing_node", "extra_relation")
            ),
            ("llm_node_f1", "llm_relation_f1"),
        )
        self.assertEqual(
            selected_group_required_metrics(group("extra_node")),
            ("llm_node_f1",),
        )
        self.assertEqual(
            selected_group_required_metrics(group("missing_relation")),
            ("llm_relation_f1",),
        )
        self.assertEqual(
            selected_group_evidence_family(group("syntax_error")),
            "compile",
        )
        self.assertEqual(
            selected_group_evidence_family(group("compile_error")),
            "compile",
        )
        mixed_diagnostic_group = group("syntax_error", "compile_error")
        self.assertEqual(
            selected_group_evidence_family(mixed_diagnostic_group),
            "compile",
        )
        self.assertEqual(
            selected_group_required_metrics(mixed_diagnostic_group),
            ("plantuml_compilation_pass_rate",),
        )
        self.assertEqual(
            validate_selected_group_eligibility(mixed_diagnostic_group),
            [],
        )

    def test_required_metric_routing_rejects_missing_or_unknown_anchor_kind(self):
        for anchor_kind in (None, "unsupported_kind"):
            selected_group = {
                "members": [
                    {
                        "finding_id": 1,
                        "status": "actionable",
                        "anchor_kind": anchor_kind,
                        "matching_quality": "bijective",
                    }
                ]
            }

            self.assertTrue(validate_selected_group_eligibility(selected_group))
            with self.assertRaisesRegex(ValueError, "supported finding anchor kinds"):
                selected_group_required_metrics(selected_group)

    def test_generic_only_batch_skips_failure_analysis_llm(self):
        class Client:
            def chat(self, messages, **kwargs):
                raise AssertionError("generic-only batch must not call Failure Analysis")

        args = SimpleNamespace(
            failure_analysis_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "failure_analysis_selector_v2.md"
            ),
            analysis_temperature=0.0,
            analysis_max_tokens=1024,
            analysis_thinking="disabled",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = analyze_failures(
                current_prompt="Prompt",
                records=[
                    record(
                        "c1",
                        compile_errors=["Some diagram description contains errors"],
                    )
                ],
                summary={},
                args=args,
                llm_client=Client(),
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                raw_output_path=root / "raw.txt",
                rejected_patterns_path=root / "rejected.json",
                state_dir=root,
                iteration=1,
                batch_id=1,
                generation_run="run",
            )

        self.assertIsNotNone(result.normalized_payload)
        self.assertEqual(result.normalized_payload["errors"][0]["status"], "uncertain")

    def test_detailed_compiler_precedes_syntax_but_both_follow_semantic_findings(self):
        payload = build_failure_analysis_input(
            [
                record(
                    "c1",
                    missing_nodes=["Missing"],
                    extra_nodes=["Extra"],
                    missing_relations=[{"from": "A", "to": "B", "type": "sequential"}],
                    extra_relations=[{"from": "X", "to": "Y", "type": "conditional"}],
                    compile_errors=["ERROR at line 3"],
                    syntax_errors=["Missing @enduml"],
                )
            ],
            generation_run="run",
            iteration=1,
            batch_id=1,
            finding_budget=6,
        )
        kinds = [
            finding["anchor_kind"]
            for case in payload["cases"]
            for finding in case["findings"]
        ]
        self.assertEqual(
            kinds,
            [
                "missing_node",
                "extra_node",
                "missing_relation",
                "extra_relation",
                "compile_error",
                "syntax_error",
            ],
        )

    def test_current_anchor_ambiguity_still_blocks_actionable(self):
        matching = {
            "nodes": {
                "tp": [{"pred": "Open", "gt": "Open database"}],
                "fn": ["Open database"],
                "fp": [],
            },
            "relations": {"tp": [], "fn": [], "fp": []},
        }
        input_payload = build_failure_analysis_input(
            [record("c1", missing_nodes=["Open database"], matching=matching)],
            generation_run="run",
            iteration=1,
            batch_id=1,
        )
        finding_id = input_payload["cases"][0]["findings"][0]["finding_id"]
        result = validate_failure_errors(
            {
                "schema_version": "failure-errors-v2",
                "errors": [
                    {
                        "finding_id": finding_id,
                        "status": "actionable",
                        "primary_finding_id": None,
                        "requirement_quote": "The user opens the database",
                        "error_summary": "Missing action.",
                        "causal_rationale": "The action appears missing.",
                    }
                ],
            },
            input_payload=input_payload,
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("ambiguous", " ".join(result.rejected_patterns[0]["errors"]))

    def test_secondary_must_link_to_actionable_primary_and_reaches_selector_as_support(self):
        input_payload = build_failure_analysis_input(
            [
                record(
                    "c1",
                    requirement="Open database and save database.",
                    missing_nodes=["Open database", "Save database"],
                )
            ],
            generation_run="run",
            iteration=1,
            batch_id=1,
        )
        findings = input_payload["cases"][0]["findings"]
        primary_id, secondary_id = [item["finding_id"] for item in findings]
        result = validate_failure_errors(
            {
                "schema_version": "failure-errors-v2",
                "errors": [
                    {
                        "finding_id": primary_id,
                        "status": "actionable",
                        "primary_finding_id": None,
                        "requirement_quote": "Open database",
                        "error_summary": "The open action is missing.",
                        "causal_rationale": "The requirement states the action.",
                    },
                    {
                        "finding_id": secondary_id,
                        "status": "secondary",
                        "primary_finding_id": primary_id,
                        "requirement_quote": "save database",
                        "error_summary": "The save action is also absent.",
                        "causal_rationale": "It depends on the same omitted sequence.",
                    },
                ],
            },
            input_payload=input_payload,
        )
        self.assertIsNotNone(result.normalized_payload)
        selector_payload = _selector_input(result.normalized_payload["errors"])
        self.assertEqual(len(selector_payload["errors"]), 1)
        self.assertEqual(
            selector_payload["errors"][0]["secondary_errors"][0]["finding_id"],
            secondary_id,
        )

    def test_selector_requires_a_complete_partition_and_derives_group_id(self):
        compact = {
            "schema_version": "error-selector-input-v2",
            "errors": [
                {"finding_id": 1},
                {"finding_id": 2},
            ],
            "_full_errors": [
                {"finding_id": 1, "finding_key": "key_a", "dataset": "d", "case_id": "a", "batch_id": 1},
                {"finding_id": 2, "finding_key": "key_b", "dataset": "d", "case_id": "b", "batch_id": 2},
            ],
        }
        output = {
            "schema_version": "error-selector-v2",
            "error_groups": [
                {
                    "local_group_id": "g1",
                    "finding_ids": [1, 2],
                    "group_summary": "Explicit actions are missing.",
                    "shared_cause": "The requirements state actions absent from the diagrams.",
                }
            ],
            "selection_status": "selected",
            "selected_group_id": "g1",
            "selection_rationale": "The group is narrow and requirement-grounded.",
        }
        normalized, errors = validate_selector_output(output, input_payload=compact)
        self.assertEqual(errors, [])
        self.assertIsNotNone(normalized)
        self.assertTrue(normalized["selected_group_id"].startswith("group_"))
        self.assertEqual(normalized["selected_group"]["supporting_case_count"], 2)
        first_group_id = normalized["selected_group_id"]

        other_epoch = json.loads(json.dumps(compact))
        other_epoch["_full_errors"][0]["finding_key"] = "other_key_a"
        other_epoch["_full_errors"][1]["finding_key"] = "other_key_b"
        other_normalized, other_errors = validate_selector_output(
            output, input_payload=other_epoch
        )
        self.assertEqual(other_errors, [])
        self.assertNotEqual(first_group_id, other_normalized["selected_group_id"])

        output["error_groups"][0]["finding_ids"] = [1]
        normalized, errors = validate_selector_output(output, input_payload=compact)
        self.assertIsNone(normalized)
        self.assertTrue(any("omitted" in error for error in errors))

    def test_selector_requires_selected_group_to_be_first_priority(self):
        compact = {
            "schema_version": "error-selector-input-v2",
            "errors": [{"finding_id": 1}, {"finding_id": 2}],
            "_full_errors": [
                {"finding_id": 1, "finding_key": "key_a"},
                {"finding_id": 2, "finding_key": "key_b"},
            ],
        }
        output = {
            "schema_version": "error-selector-v2",
            "error_groups": [
                {
                    "local_group_id": "g1",
                    "finding_ids": [1],
                    "group_summary": "First group.",
                    "shared_cause": "First cause.",
                },
                {
                    "local_group_id": "g2",
                    "finding_ids": [2],
                    "group_summary": "Second group.",
                    "shared_cause": "Second cause.",
                },
            ],
            "selection_status": "selected",
            "selected_group_id": "g2",
            "selection_rationale": "The second group was selected out of order.",
        }

        normalized, errors = validate_selector_output(output, input_payload=compact)

        self.assertIsNone(normalized)
        self.assertIn(
            "selected_group_id must reference the first priority-ordered group",
            errors,
        )

    def test_selector_may_abstain_after_returning_a_complete_partition(self):
        compact = {
            "schema_version": "error-selector-input-v2",
            "errors": [{"finding_id": 1}],
            "_full_errors": [
                {"finding_id": 1, "finding_key": "key_a", "dataset": "d", "case_id": "a", "batch_id": 1}
            ],
        }
        normalized, errors = validate_selector_output(
            {
                "schema_version": "error-selector-v2",
                "error_groups": [
                    {
                        "local_group_id": "g1",
                        "finding_ids": [1],
                        "group_summary": "One isolated error.",
                        "shared_cause": "No broader coherent cause is established.",
                    }
                ],
                "selection_status": "abstain",
                "selected_group_id": "",
                "selection_rationale": "No group supports one narrow refinement.",
            },
            input_payload=compact,
        )
        self.assertEqual(errors, [])
        self.assertEqual(normalized["selection_status"], "abstain")
        self.assertIsNone(normalized["selected_group"])

    def test_selector_repairs_invalid_partition_once(self):
        responses = [
            {
                "schema_version": "error-selector-v2",
                "error_groups": [
                    {
                        "local_group_id": "g1",
                        "finding_ids": [999],
                        "group_summary": "Invalid reference.",
                        "shared_cause": "The first attempt copied the wrong ID.",
                    }
                ],
                "selection_status": "selected",
                "selected_group_id": "g1",
                "selection_rationale": "This attempt is invalid.",
            },
            {
                "schema_version": "error-selector-v2",
                "error_groups": [
                    {
                        "local_group_id": "g1",
                        "finding_ids": [1],
                        "group_summary": "One explicit action is missing.",
                        "shared_cause": "The requirement states an action absent from the diagram.",
                    }
                ],
                "selection_status": "selected",
                "selected_group_id": "g1",
                "selection_rationale": "The singleton is narrow and grounded.",
            },
        ]

        class Client:
            payloads = []

            def chat(self, messages, **kwargs):
                self.payloads.append(json.loads(messages[1]["content"]))
                return json.dumps(responses[len(self.payloads) - 1])

        client = Client()
        args = SimpleNamespace(
            error_selector_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "error_selector_v4.md"
            ),
            selector_temperature=0.0,
            selector_max_tokens=1024,
            selector_thinking="disabled",
        )
        error = {
            "finding_id": 1,
            "finding_key": "stable_key_1",
            "status": "actionable",
            "primary_finding_id": None,
            "dataset": "d",
            "case_id": "c1",
            "batch_id": 1,
            "anchor_kind": "missing_node",
            "error_anchor": "Open database",
            "requirement_quote": "Open database",
            "error_summary": "An explicit action is missing.",
            "causal_rationale": "The requirement states the action.",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = select_error_group(
                errors=[error],
                args=args,
                llm_client=client,
                output_input_path=root / "selector.input.json",
                output_path=root / "selector.output.json",
                state_dir=root,
                iteration=1,
            )
            saved_input = json.loads((root / "selector.input.json").read_text(encoding="utf-8"))

        self.assertIsNotNone(result)
        self.assertEqual(len(client.payloads), 2)
        self.assertEqual(client.payloads[1]["schema_version"], "error-selector-repair-v1")
        self.assertTrue(
            any("unknown" in item for item in client.payloads[1]["validation_errors"])
        )
        self.assertNotIn("_full_errors", saved_input)
        self.assertEqual(saved_input["errors"][0]["finding_id"], 1)

    def test_blank_prompt_gap_and_rewriter_plan_use_exact_replacement(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        localization, errors = _validate_prompt_gap_localization(
            {
                "schema_version": "prompt-gap-localization-v2",
                "localization_status": "localized",
                "prompt_gap": "missing",
                "section": "rule",
                "operation": "replace_existing",
                "existing_prompt_quote": "(None)",
                "rationale": "The blank rule section lacks this guidance.",
                "group_consistency": "coherent",
                "member_checks": [
                    {"finding_id": 1, "compatible": True, "conflict_reason": ""}
                ],
                "shared_repair": {
                    "input_trigger": "An explicit performed action is stated.",
                    "structural_operation": "Create one activity for the action.",
                    "preservation_boundary": "Preserve non-action context.",
                },
            },
            current_prompt=prompt,
            selected_finding_ids=[1],
        )
        self.assertEqual(errors, [])
        editor_plan = {
            "schema_version": "prompt-edit-plan-v2",
            "intent": "Add the selected behavior.",
            "positive_trigger": "Represent each explicitly stated action as an activity.",
            "negative_boundary": "Do not invent actions not stated by the requirement.",
            "change_instruction": "Write the canonical rule.",
        }
        plan = build_rewriter_plan(
            localization=localization,
            editor_plan=editor_plan,
        )
        rule = f"{editor_plan['positive_trigger']} {editor_plan['negative_boundary']}"
        candidate, apply_errors = apply_prompt_revision_fragment(prompt, plan, rule)
        self.assertEqual(apply_errors, [])
        self.assertNotIn("## rule\n(None)", candidate)
        self.assertIn(rule, candidate)


    def test_prompt_gap_localization_repairs_invalid_schema_output(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        responses = [
            {
                "schema_version": "prompt-gap-localization-v2",
                "localization_status": "localized",
                "prompt_gap": "missing",
                "section": "workflow",
                "operation": "replace_existing",
                "existing_prompt_quote": "(None)",
                "rationale": "The first mapping is incompatible.",
                "group_consistency": "coherent",
                "member_checks": [
                    {"finding_id": 999, "compatible": True, "conflict_reason": ""}
                ],
                "shared_repair": {
                    "input_trigger": "An explicit action is stated.",
                    "structural_operation": "Represent the action once.",
                    "preservation_boundary": "Preserve contextual descriptions.",
                },
                "unsupported_field": "invalid",
            },
            {
                "schema_version": "prompt-gap-localization-v2",
                "localization_status": "localized",
                "prompt_gap": "missing",
                "section": "workflow",
                "operation": "replace_existing",
                "existing_prompt_quote": "(None)",
                "rationale": "The blank workflow lacks guidance for the selected cause.",
                "group_consistency": "coherent",
                "member_checks": [
                    {"finding_id": 1, "compatible": True, "conflict_reason": ""}
                ],
                "shared_repair": {
                    "input_trigger": "An explicit action is stated.",
                    "structural_operation": "Represent the action once.",
                    "preservation_boundary": "Preserve contextual descriptions.",
                },
            },
        ]

        class Client:
            payloads = []

            def chat(self, messages, **kwargs):
                self.payloads.append(json.loads(messages[1]["content"]))
                return json.dumps(responses[len(self.payloads) - 1])

        args = SimpleNamespace(
            error_localization_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_gap_localization_v2.md"
            ),
            localization_temperature=0.0,
            localization_max_tokens=1024,
            localization_thinking="disabled",
        )
        group = {
            "group_id": "group_extra",
            "group_summary": "An extra node is introduced.",
            "shared_cause": "The prediction introduces an unsupported extra node.",
            "members": [
                {
                    "finding_id": 1,
                    "anchor_kind": "extra_node",
                    "error_anchor": "Load the data",
                    "requirement_quote": "Load the data.",
                    "error_summary": "Extra node.",
                    "causal_rationale": "The selected cause is uncertain.",
                    "secondary_errors": [],
                }
            ],
            "representative_errors": [
                {
                    "finding_id": 1,
                    "anchor_kind": "extra_node",
                    "error_anchor": "Load the data",
                    "requirement_quote": "Load the data.",
                    "error_summary": "Extra node.",
                    "causal_rationale": "The selected cause is uncertain.",
                }
            ],
        }
        client = Client()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = localize_selector_group(
                current_prompt=prompt,
                selected_group=group,
                args=args,
                llm_client=client,
                output_input_path=root / "localization.input.json",
                output_path=root / "localization.output.json",
                state_dir=root,
                iteration=1,
                recurrence={
                    "match_basis": "same_base_prompt_and_exact_finding_keys",
                    "same_prompt_occurrences": 2,
                    "prior_already_covered_count": 1,
                    "previous_outcomes": ["already_covered"],
                },
            )
            saved_input = json.loads(
                (root / "localization.input.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result["localization_status"], "localized")
        self.assertEqual(len(client.payloads), 2)
        self.assertEqual(client.payloads[1]["schema_version"], "prompt-gap-localization-repair-v2")
        self.assertEqual(saved_input["exact_recurrence"]["same_prompt_occurrences"], 2)
        self.assertEqual(saved_input["schema_version"], "prompt-gap-localization-input-v2")
        self.assertEqual(
            saved_input["selected_error_group"]["member_evidence"][0]["finding_id"],
            1,
        )

    def test_incoherent_localization_requires_member_conflict_and_no_edit(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        localization, errors = _validate_prompt_gap_localization(
            {
                "schema_version": "prompt-gap-localization-v2",
                "localization_status": "no_prompt_gap",
                "prompt_gap": "not_applicable",
                "section": "",
                "operation": "none",
                "existing_prompt_quote": "",
                "rationale": "The members require incompatible node operations.",
                "group_consistency": "incoherent",
                "member_checks": [
                    {
                        "finding_id": 1,
                        "compatible": True,
                        "conflict_reason": "",
                    },
                    {
                        "finding_id": 2,
                        "compatible": False,
                        "conflict_reason": (
                            "This shared-head object list must remain one action, while "
                            "the other member contains independently performed verbs."
                        ),
                    },
                ],
                "shared_repair": {
                    "input_trigger": "",
                    "structural_operation": "",
                    "preservation_boundary": "",
                },
            },
            current_prompt=prompt,
            selected_finding_ids=[1, 2],
        )

        self.assertEqual(errors, [])
        self.assertEqual(localization["group_consistency"], "incoherent")
        self.assertEqual(localization["localization_status"], "no_prompt_gap")

    def test_localization_rejects_missing_duplicate_and_unknown_member_checks(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        base = {
            "schema_version": "prompt-gap-localization-v2",
            "localization_status": "localized",
            "prompt_gap": "missing",
            "section": "rule",
            "operation": "replace_existing",
            "existing_prompt_quote": "(None)",
            "rationale": "Both members share one repair.",
            "group_consistency": "coherent",
            "member_checks": [
                {"finding_id": 1, "compatible": True, "conflict_reason": ""},
                {"finding_id": 2, "compatible": True, "conflict_reason": ""},
            ],
            "shared_repair": {
                "input_trigger": "Independent performed verbs are stated.",
                "structural_operation": "Keep each performed action distinct.",
                "preservation_boundary": "Do not split shared-head object lists.",
            },
        }
        invalid_checks = {
            "missing": [base["member_checks"][0]],
            "duplicate": [base["member_checks"][0], base["member_checks"][0]],
            "unknown": [base["member_checks"][0], {"finding_id": 3, "compatible": True, "conflict_reason": ""}],
        }

        for label, checks in invalid_checks.items():
            with self.subTest(label=label):
                payload = {**base, "member_checks": checks}
                localization, errors = _validate_prompt_gap_localization(
                    payload,
                    current_prompt=prompt,
                    selected_finding_ids=[1, 2],
                )
                self.assertIsNone(localization)
                self.assertTrue(errors)

        conflict_payload = {
            **base,
            "group_consistency": "incoherent",
            "member_checks": [
                base["member_checks"][0],
                {
                    "finding_id": 2,
                    "compatible": False,
                    "conflict_reason": "The structural operation conflicts.",
                },
            ],
        }
        localization, errors = _validate_prompt_gap_localization(
            conflict_payload,
            current_prompt=prompt,
            selected_finding_ids=[1, 2],
        )
        self.assertIsNone(localization)
        self.assertTrue(any("must use localization_status=no_prompt_gap" in item for item in errors))

    def test_exact_no_prompt_gap_history_filters_only_same_prompt_and_findings(self):
        groups = [
            {
                "group_id": "group_1",
                "members": [{"finding_key": "finding_1"}],
            },
            {
                "group_id": "group_2",
                "members": [{"finding_key": "finding_2"}],
            },
        ]
        registry = {
            "version": "candidate-registry-v1",
            "entries": [],
            "group_attempts": [],
        }
        record_group_attempt(
            registry,
            iteration=1,
            attempt=1,
            base_prompt_hash="base_hash",
            group_id="group_1",
            finding_keys=["finding_1"],
            outcome="no_prompt_gap",
            rejection_reasons=["no_prompt_gap"],
        )

        eligible, filtered = filter_candidate_groups_by_attempt_history(
            groups,
            registry=registry,
            base_prompt_hash="base_hash",
        )
        other_prompt_eligible, other_prompt_filtered = (
            filter_candidate_groups_by_attempt_history(
                groups,
                registry=registry,
                base_prompt_hash="other_base_hash",
            )
        )

        self.assertEqual([group["group_id"] for group in eligible], ["group_2"])
        self.assertEqual([group["group_id"] for group in filtered], ["group_1"])
        self.assertEqual(other_prompt_eligible, groups)
        self.assertEqual(other_prompt_filtered, [])

    def test_group_incoherent_skips_downstream_stages_and_continues(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        args = build_parser().parse_args(
            [
                "--iterations",
                "1",
                "--analysis-batch-size",
                "10",
                "--max-candidate-attempts-per-epoch",
                "2",
            ]
        )
        cases = [
            Case(
                dataset="data",
                case_id="c1",
                content="Open and save the record.",
                gold_plantuml="G",
            ),
            Case(
                dataset="data",
                case_id="c2",
                content="Enter the name and description.",
                gold_plantuml="G",
            ),
        ]

        members = [
            {
                "finding_id": index,
                "finding_key": f"finding_{index}",
                "status": "actionable",
                "primary_finding_id": None,
                "dataset": "data",
                "case_id": f"c{index}",
                "batch_id": 1,
                "anchor_kind": "missing_node",
                "error_anchor": f"Action {index}",
                "matching_quality": "bijective",
                "requirement_quote": f"Action {index}",
                "error_summary": f"Action {index} is missing.",
                "causal_rationale": f"The requirement states action {index}.",
            }
            for index in (1, 2)
        ]

        def batch_result(**kwargs):
            return EpochBatchResult(
                batch_index=1,
                global_update_step=1,
                records=[],
                summary={},
                batch_summary={"batch_index": 1},
                error_observations=members,
                valid_pattern_count=2,
            )

        selector_result = {
            "schema_version": "error-selector-v2",
            "selection_status": "selected",
            "selected_group_id": "group_1",
            "selection_rationale": "Priority order.",
            "error_groups": [
                {
                    "group_id": f"group_{index}",
                    "group_summary": f"Group {index}",
                    "shared_cause": f"Cause {index}",
                    "finding_ids": [index],
                    "members": [member],
                }
                for index, member in enumerate(members, start=1)
            ],
            "selected_group": None,
        }
        localizations = [
            {
                "schema_version": "prompt-gap-localization-v2",
                "localization_status": "no_prompt_gap",
                "prompt_gap": "not_applicable",
                "section": "",
                "operation": "none",
                "existing_prompt_quote": "",
                "rationale": "The member conflicts with the proposed shared repair.",
                "group_consistency": "incoherent",
                "member_checks": [
                    {
                        "finding_id": 1,
                        "compatible": False,
                        "conflict_reason": "The structural operation conflicts.",
                    }
                ],
                "shared_repair": {
                    "input_trigger": "",
                    "structural_operation": "",
                    "preservation_boundary": "",
                },
            },
            {
                "schema_version": "prompt-gap-localization-v2",
                "localization_status": "already_covered",
                "prompt_gap": "already_covered",
                "section": "output",
                "operation": "none",
                "existing_prompt_quote": "Output PlantUML code only.",
                "rationale": "Existing guidance covers the member.",
                "group_consistency": "coherent",
                "member_checks": [
                    {"finding_id": 2, "compatible": True, "conflict_reason": ""}
                ],
                "shared_repair": {
                    "input_trigger": "The performed action is explicit.",
                    "structural_operation": "Represent the action.",
                    "preservation_boundary": "Preserve shared-head object lists.",
                },
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work = root / "work.md"
            work.write_text(prompt, encoding="utf-8")
            with patch("run.process_epoch_batch", side_effect=batch_result), patch(
                "run.select_error_group", return_value=selector_result
            ), patch(
                "run.localize_selector_group", side_effect=localizations
            ) as localize, patch("run.propose_selector_edit") as editor, patch(
                "run.evaluate_gate"
            ) as gate:
                run_training_iterations(
                    args=args,
                    llm_client=object(),
                    train_cases=cases,
                    source_dataset_counts={"bp": len(cases)},
                    run_dir=root,
                    work_prompt_path=work,
                    label="selector-test",
                    validation_cases=cases,
                    confirmation_cases=cases,
                )
            registry = json.loads(
                (root / "candidate_registry.json").read_text(encoding="utf-8")
            )

        self.assertEqual(localize.call_count, 2)
        editor.assert_not_called()
        gate.assert_not_called()
        self.assertEqual(
            [item["outcome"] for item in registry["group_attempts"]],
            ["group_incoherent", "already_covered"],
        )

    def test_exact_group_incoherent_history_is_filtered(self):
        group = {
            "group_id": "group_1",
            "members": [{"finding_key": "finding_1"}],
        }
        registry = {
            "version": "candidate-registry-v1",
            "entries": [],
            "group_attempts": [],
        }
        record_group_attempt(
            registry,
            iteration=1,
            attempt=1,
            base_prompt_hash="base_hash",
            group_id="group_1",
            finding_keys=["finding_1"],
            outcome="group_incoherent",
            rejection_reasons=["group_incoherent"],
        )

        eligible, filtered = filter_candidate_groups_by_attempt_history(
            [group], registry=registry, base_prompt_hash="base_hash"
        )
        other_prompt, _ = filter_candidate_groups_by_attempt_history(
            [group], registry=registry, base_prompt_hash="other_hash"
        )

        self.assertEqual(eligible, [])
        self.assertEqual(filtered[0]["prior_terminal_outcomes"], ["group_incoherent"])
        self.assertEqual(other_prompt, [group])

    def test_localization_prompt_requires_member_level_conflict_for_no_gap(self):
        prompt_text = (
            PROJECT_DIR / "prompt_workspace" / "prompt_gap_localization_v2.md"
        ).read_text(encoding="utf-8")
        self.assertIn("member_evidence", prompt_text)
        self.assertIn("one shared input trigger, structural operation, and preservation boundary", prompt_text)
        self.assertIn("concrete member conflict or evidence limitation", prompt_text)
        self.assertIn("exactly one `member_checks` item", prompt_text)
        self.assertIn('"schema_version": "prompt-gap-localization-v2"', prompt_text)
        self.assertIn("complete `shared_repair`", prompt_text)
        self.assertIn("evidence-bound semantic applicability test", prompt_text)
        self.assertIn("not sufficient by themselves", prompt_text)
        self.assertIn("unspecified order or concurrency must remain unspecified", prompt_text)
        self.assertIn("Do not write final replacement or rule text", prompt_text)
        self.assertNotIn(
            "Never write replacement text, a trigger, a boundary",
            prompt_text,
        )

    def test_localization_prompt_distinguishes_full_from_related_coverage(self):
        prompt_text = (
            PROJECT_DIR / "prompt_workspace" / "prompt_gap_localization_v2.md"
        ).read_text(encoding="utf-8")
        self.assertIn("prove coverage against every member", prompt_text)
        self.assertIn("observed input-side cue", prompt_text)
        self.assertIn("same desired structural correction", prompt_text)
        self.assertIn("Shared terminology or a related topic is not coverage", prompt_text)
        self.assertIn("even without exact recurrence evidence", prompt_text)
        self.assertIn(
            "Never return `no_prompt_gap` because existing guidance covers the error",
            prompt_text,
        )
        self.assertIn(
            "partial or ambiguous coverage requires `localized + ambiguous + replace_existing`",
            prompt_text,
        )

    def test_editor_prompt_requires_operational_trigger_and_structure_boundaries(self):
        prompt_text = (
            PROJECT_DIR / "prompt_workspace" / "prompt_editor_selector_v2.md"
        ).read_text(encoding="utf-8")

        self.assertIn("operational applicability test", prompt_text)
        self.assertIn("isolated keyword is never sufficient by itself", prompt_text)
        self.assertIn("independently performed verb phrases", prompt_text)
        self.assertIn("shared-head objects, participants, field lists, and compound verbs", prompt_text)
        self.assertIn("Ordinary `and`, commas, bullets, or headings do not imply concurrency", prompt_text)
        self.assertIn("explicit simultaneous, concurrent, or in-parallel semantics", prompt_text)
        self.assertIn("non-branching modifier", prompt_text)
        self.assertIn("each exactly once as a contiguous span", prompt_text)
        self.assertIn("Preserve wording and word order", prompt_text)
        self.assertIn("only case, punctuation, and whitespace may change", prompt_text)

    def test_rewriter_prompt_preserves_canonical_spans_exactly_once(self):
        prompt_text = (
            PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_selector_v1.md"
        ).read_text(encoding="utf-8")

        self.assertIn("exactly once as contiguous spans", prompt_text)
        self.assertIn("Preserve wording and word order", prompt_text)
        self.assertIn("only case, punctuation, and whitespace may change", prompt_text)

    def test_exact_already_covered_history_builds_recurrence_context(self):
        history = [
            {"iteration": 1, "outcome": "gate1_rejected"},
            {"iteration": 2, "outcome": "already_covered"},
        ]

        recurrence = exact_already_covered_recurrence(history)

        self.assertEqual(recurrence["same_prompt_occurrences"], 3)
        self.assertEqual(recurrence["prior_already_covered_count"], 1)
        self.assertEqual(
            recurrence["previous_outcomes"],
            ["gate1_rejected", "already_covered"],
        )
        self.assertIsNone(
            exact_already_covered_recurrence(
                [{"iteration": 1, "outcome": "gate1_rejected"}]
            )
        )

    def test_new_pipeline_defaults(self):
        args = build_parser().parse_args([])
        self.assertEqual(args.candidate_application_mode, "auto")
        self.assertFalse(args.gate2)
        self.assertEqual(args.failure_analysis_prompt_path.name, "failure_analysis_selector_v2.md")
        self.assertEqual(args.error_selector_prompt_path.name, "error_selector_v4.md")
        self.assertEqual(args.error_localization_prompt_path.name, "prompt_gap_localization_v2.md")
        self.assertEqual(args.max_candidate_attempts_per_epoch, 3)
        self.assertEqual(args.prompt_editor_prompt_path.name, "prompt_editor_selector_v2.md")
        self.assertEqual(args.prompt_rewriter_prompt_path.name, "prompt_rewriter_selector_v1.md")
        resolve_pipeline_defaults(args)
        self.assertEqual(args.candidate_application_mode, "cumulative")

    def test_editor_v2_freezes_trigger_and_boundary_without_external_mapping(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        responses = [
            {
                "schema_version": "prompt-edit-plan-v2",
                "intent": "Repair the selected behavior.",
                "positive_trigger": "Fix the prediction's missing node.",
                "negative_boundary": "Do not invent behavior.",
                "change_instruction": "Write one narrow rule.",
            },
            {
                "schema_version": "prompt-edit-plan-v2",
                "intent": "Represent the selected stated behavior.",
                "positive_trigger": "Represent each explicitly stated performed action as an activity.",
                "negative_boundary": "Do not create activities for unstated or static context.",
                "change_instruction": "Preserve valid guidance and add only this boundary.",
            },
        ]

        class Client:
            payloads = []

            def chat(self, messages, **kwargs):
                self.payloads.append(json.loads(messages[1]["content"]))
                return json.dumps(responses[len(self.payloads) - 1])

        args = SimpleNamespace(
            prompt_editor_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_editor_selector_v2.md"
            ),
            editor_temperature=0.0,
            editor_max_tokens=1024,
            editor_thinking="disabled",
        )
        localization = {
            "schema_version": "prompt-gap-localization-v1",
            "localization_status": "localized",
            "prompt_gap": "missing",
            "section": "rule",
            "operation": "replace_existing",
            "existing_prompt_quote": "(None)",
            "rationale": "The rule is absent.",
        }
        group = {
            "group_id": "group_1",
            "group_summary": "An explicit action is missing.",
            "shared_cause": "The requirement states an action that is absent.",
            "representative_errors": [],
        }
        client = Client()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = propose_selector_edit(
                current_prompt=prompt,
                selected_group=group,
                localization=localization,
                args=args,
                llm_client=client,
                output_input_path=root / "editor.input.json",
                output_path=root / "editor.output.json",
                state_dir=root,
                iteration=1,
            )
            saved_input = json.loads(
                (root / "editor.input.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result["schema_version"], "prompt-edit-plan-v2")
        self.assertEqual(len(client.payloads), 2)
        self.assertEqual(client.payloads[1]["schema_version"], "prompt-edit-plan-repair-v1")
        self.assertNotIn("repair", saved_input)

    def test_editor_retry_names_the_required_canonical_fragment(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        input_trigger = "A requirement stating a continuous action"
        structural_operation = "Generate one activity node"
        preservation_boundary = "Do not invent an unstated loop condition"
        responses = [
            {
                "schema_version": "prompt-edit-plan-v2",
                "intent": "Represent the continuous action once.",
                "positive_trigger": (
                    "When a requirement states a continuous action, generate one activity node."
                ),
                "negative_boundary": preservation_boundary,
                "change_instruction": "Write one narrow rule.",
            },
            {
                "schema_version": "prompt-edit-plan-v2",
                "intent": "Represent the continuous action once.",
                "positive_trigger": f"{input_trigger}; {structural_operation}.",
                "negative_boundary": preservation_boundary,
                "change_instruction": "Write one narrow rule.",
            },
        ]

        class Client:
            payloads = []

            def chat(self, messages, **kwargs):
                self.payloads.append(json.loads(messages[1]["content"]))
                return json.dumps(responses[len(self.payloads) - 1])

        localization = {
            "localization_status": "localized",
            "section": "rule",
            "shared_repair": {
                "input_trigger": input_trigger,
                "structural_operation": structural_operation,
                "preservation_boundary": preservation_boundary,
            },
        }
        args = SimpleNamespace(
            prompt_editor_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_editor_selector_v2.md"
            ),
            editor_temperature=0.0,
            editor_max_tokens=1024,
            editor_thinking="disabled",
        )
        client = Client()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = propose_selector_edit(
                current_prompt=prompt,
                selected_group={
                    "group_id": "group_1",
                    "group_summary": "A continuous action is duplicated.",
                    "shared_cause": "The action is represented as an extra loop condition.",
                    "representative_errors": [],
                },
                localization=localization,
                args=args,
                llm_client=client,
                output_input_path=root / "editor.input.json",
                output_path=root / "editor.output.json",
                state_dir=root,
                iteration=1,
            )

        self.assertIsNotNone(result)
        self.assertEqual(len(client.payloads), 2)
        retry_payload = client.payloads[1]
        self.assertTrue(
            any(input_trigger in error for error in retry_payload["validation_errors"])
        )
        self.assertIn("Do not paraphrase", retry_payload["repair_instruction"])

    def test_diagnostic_apply_requires_a_valid_measurement(self):
        decision = selector_application_decision(
            mode="diagnostic-apply",
            candidate_valid=True,
            gate_evaluated=True,
            acceptance_decision={
                "accepted": True,
                "evaluation_valid": False,
                "invalid_reasons": ["infrastructure_error"],
            },
        )
        self.assertFalse(decision["measurement_valid"])
        self.assertFalse(decision["applied"])

    def test_rewriter_receives_only_the_frozen_target_interface(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\nKeep valid guidance.\n\n"
            "## rule\n(None)\n"
        )
        positive = "Map each explicitly stated action to an activity."
        negative = "Do not invent actions that are not stated."
        revision_plan = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "replace_existing",
                    "text_to_modify": "(None)",
                    "intent": "Cover one explicit action.",
                    "change_instruction": "Use the frozen trigger and boundary.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }

        class Client:
            payload = None

            def chat(self, messages, **kwargs):
                self.payload = json.loads(messages[1]["content"])
                return json.dumps({"rule_text": f"{positive} {negative}"})

        client = Client()
        args = SimpleNamespace(
            prompt_rewriter_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_selector_v1.md"
            ),
            editor_temperature=0.0,
            editor_max_tokens=512,
            editor_thinking="disabled",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = rewrite_prompt(
                current_prompt=prompt,
                revision_plan=revision_plan,
                args=args,
                llm_client=client,
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                state_dir=root,
                iteration=1,
            )

        self.assertIsNotNone(candidate)
        self.assertEqual(
            set(client.payload),
            {
                "target_section",
                "target_section_text",
                "operation",
                "existing_prompt_quote",
                "editor_plan",
                "positive_trigger",
                "negative_boundary",
            },
        )
        self.assertNotIn("current_prompt", client.payload)
        self.assertNotIn("revision_plan", client.payload)

    def test_rewriter_rejects_missing_canonical_fragments_without_appending_them(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\nKeep valid guidance.\n\n"
            "## rule\n(None)\n"
        )
        positive = "Map each explicitly stated action to an activity."
        negative = "Do not invent actions that are not stated."
        revision_plan = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "replace_existing",
                    "text_to_modify": "(None)",
                    "intent": "Cover one explicit action.",
                    "change_instruction": "Use the frozen trigger and boundary.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }

        class Client:
            payloads = []

            def chat(self, messages, **kwargs):
                self.payloads.append(json.loads(messages[1]["content"]))
                return json.dumps({"rule_text": "Map the action concisely."})

        args = SimpleNamespace(
            prompt_rewriter_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_selector_v1.md"
            ),
            editor_temperature=0.0,
            editor_max_tokens=512,
            editor_thinking="disabled",
        )
        client = Client()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = rewrite_prompt(
                current_prompt=prompt,
                revision_plan=revision_plan,
                args=args,
                llm_client=client,
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                state_dir=root,
                iteration=1,
            )

        self.assertIsNone(candidate)
        self.assertEqual(len(client.payloads), 2)
        retry_payload = client.payloads[1]
        self.assertTrue(
            any(positive in error for error in retry_payload["validation_errors"])
        )
        self.assertTrue(
            any(negative in error for error in retry_payload["validation_errors"])
        )
        self.assertIn("Do not paraphrase", retry_payload["repair_instruction"])

    def test_rule_sentence_count_ignores_non_terminal_period_sequences(self):
        self.assertEqual(
            rule_sentence_count(
                "A detected condition ... triggers a process. Preserve the event."
            ),
            2,
        )
        self.assertEqual(
            rule_sentence_count("Use e.g. one stated action. Preserve version 2.1."),
            2,
        )
        self.assertEqual(
            rule_sentence_count("Use i.e. one stated guard. Preserve the condition."),
            2,
        )
        self.assertEqual(rule_sentence_count("One rule. Two rules. Three rules."), 3)

    def test_rewriter_accepts_two_sentences_with_an_internal_ellipsis(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\nKeep valid guidance.\n\n"
            "## rule\n(None)\n"
        )
        positive = (
            "A requirement where a detected condition uses language such as event detected "
            "... triggers a state machine: model the condition as the trigger."
        )
        negative = "Preserve the event and the state machine invocation."
        revision_plan = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "replace_existing",
                    "text_to_modify": "(None)",
                    "intent": "Keep the detected condition as a trigger.",
                    "change_instruction": "Use the frozen trigger and boundary.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }

        class Client:
            calls = 0

            def chat(self, messages, **kwargs):
                self.calls += 1
                return json.dumps({"rule_text": f"{positive} {negative}"})

        args = SimpleNamespace(
            prompt_rewriter_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_selector_v1.md"
            ),
            editor_temperature=0.0,
            editor_max_tokens=512,
            editor_thinking="disabled",
        )
        client = Client()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = rewrite_prompt(
                current_prompt=prompt,
                revision_plan=revision_plan,
                args=args,
                llm_client=client,
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                state_dir=root,
                iteration=1,
            )

        self.assertIsNotNone(candidate)
        self.assertEqual(client.calls, 1)

    def test_rewriter_rejects_rule_with_more_than_two_sentences(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\nKeep valid guidance.\n\n"
            "## rule\n(None)\n"
        )
        positive = "Represent each explicitly stated action as an activity."
        negative = "Do not invent actions that are not stated."
        revision_plan = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "replace_existing",
                    "text_to_modify": "(None)",
                    "intent": "Cover one explicit action.",
                    "change_instruction": "Use the frozen trigger and boundary.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }

        class Client:
            calls = 0

            def chat(self, messages, **kwargs):
                self.calls += 1
                return json.dumps(
                    {
                        "rule_text": (
                            f"{positive} Add an unrelated broad exception. {negative}"
                        )
                    }
                )

        args = SimpleNamespace(
            prompt_rewriter_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_selector_v1.md"
            ),
            editor_temperature=0.0,
            editor_max_tokens=512,
            editor_thinking="disabled",
        )
        client = Client()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = rewrite_prompt(
                current_prompt=prompt,
                revision_plan=revision_plan,
                args=args,
                llm_client=client,
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                state_dir=root,
                iteration=1,
            )

        self.assertIsNone(candidate)
        self.assertEqual(client.calls, 2)

    def test_editor_scope_must_preserve_localization_shared_repair(self):
        localization = {
            "localization_status": "localized",
            "shared_repair": {
                "input_trigger": "the requirement explicitly states the action",
                "structural_operation": "represent that action as one activity",
                "preservation_boundary": "do not create activities for context",
            },
        }
        values = {
            "positive_trigger": "Represent explicit actions.",
            "negative_boundary": "Do not invent activities.",
        }
        errors = _shared_repair_contract_errors(localization, values)
        self.assertTrue(
            any(
                error.startswith(
                    "positive_trigger must contain shared_repair.input_trigger once"
                )
                and localization["shared_repair"]["input_trigger"] in error
                for error in errors
            )
        )
        self.assertTrue(
            any(
                error.startswith(
                    "negative_boundary must contain shared_repair.preservation_boundary once"
                )
                and localization["shared_repair"]["preservation_boundary"] in error
                for error in errors
            )
        )

    def test_rewriter_keeps_formally_equivalent_text_without_duplicate_append(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\nKeep valid guidance.\n\n"
            "## rule\n(None)\n"
        )
        positive = "Place each explicitly stated action after the monitoring action."
        negative = "Do not introduce loop-back relations from the monitoring action."
        revision_plan = {
            "revision_plan": [
                {
                    "section": "rule",
                    "operation": "replace_existing",
                    "text_to_modify": "(None)",
                    "intent": "Preserve sequential monitoring behavior.",
                    "change_instruction": "Keep the supplied boundaries.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }

        class Client:
            calls = 0

            def chat(self, messages, **kwargs):
                self.calls += 1
                return json.dumps(
                    {
                        "rule_text": (
                            "place each explicitly stated action after the monitoring action; "
                            "do not introduce loop-back relations from the monitoring action."
                        )
                    }
                )

        client = Client()
        args = SimpleNamespace(
            prompt_rewriter_prompt_path=(
                PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_selector_v1.md"
            ),
            editor_temperature=0.0,
            editor_max_tokens=512,
            editor_thinking="disabled",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            candidate = rewrite_prompt(
                current_prompt=prompt,
                revision_plan=revision_plan,
                args=args,
                llm_client=client,
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                state_dir=root,
                iteration=1,
            )

        self.assertIsNotNone(candidate)
        self.assertEqual(client.calls, 1)
        self.assertEqual(
            (candidate or "").lower().count("place each explicitly stated action"),
            1,
        )
        self.assertEqual(
            (candidate or "").lower().count("do not introduce loop-back relations"),
            1,
        )

    def test_diagnostic_apply_feeds_updated_prompt_to_next_epoch(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        args = build_parser().parse_args(
            [
                "--iterations",
                "2",
                "--analysis-batch-size",
                "10",
                "--candidate-application-mode",
                "diagnostic-apply",
                    "--no-gate2",
            ]
        )
        cases = [
            Case(dataset="data", case_id="c1", content="Open database.", gold_plantuml="G"),
            Case(dataset="data", case_id="c2", content="Save database.", gold_plantuml="G"),
        ]

        def batch_result(**kwargs):
            iteration = kwargs["iteration"]
            finding_id = iteration
            error = {
                "finding_id": finding_id,
                "finding_key": f"finding_key_{iteration}",
                "status": "actionable",
                "primary_finding_id": None,
                "dataset": "data",
                "case_id": f"c{iteration}",
                "batch_id": 1,
                "anchor_kind": "missing_node",
                "error_anchor": "Open database",
                "matching_quality": "bijective",
                "requirement_quote": "Open database",
                "error_summary": "An explicit action is missing.",
                "causal_rationale": "The requirement states the omitted action.",
            }
            return EpochBatchResult(
                batch_index=1,
                global_update_step=iteration,
                records=[],
                summary={},
                batch_summary={"batch_index": 1},
                failure_analysis={"schema_version": "failure-errors-v2", "errors": [error]},
                error_observations=[error],
                valid_pattern_count=1,
            )

        def selector_result(*, errors, **kwargs):
            member = errors[0]
            return {
                "schema_version": "error-selector-v2",
                "error_groups": [],
                "selection_status": "selected",
                "selected_group_id": f"group_{member['finding_id']}",
                "selection_rationale": "Narrow and grounded.",
                "selected_group": {
                    "local_group_id": "g1",
                    "group_id": f"group_{member['finding_id']}",
                    "finding_ids": [member["finding_id"]],
                    "group_summary": "Explicit actions are missing.",
                    "shared_cause": "The requirement states an omitted action.",
                    "members": [member],
                },
            }

        def localization(*, current_prompt, **kwargs):
            blank = "## rule\n(None)" in current_prompt
            return {
                "schema_version": "prompt-gap-localization-v1",
                "localization_status": "localized",
                "prompt_gap": "missing",
                "section": "rule",
                "operation": "replace_existing" if blank else "append_new",
                "existing_prompt_quote": "(None)" if blank else "",
                "rationale": "The rule is absent.",
            }

        def rewrite(*, current_prompt, revision_plan, output_path, **kwargs):
            item = revision_plan["revision_plan"][0]
            rule = f"{item['positive_trigger']} {item['negative_boundary']}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"rule_text": rule}), encoding="utf-8")
            candidate, errors = apply_prompt_revision_fragment(
                current_prompt, revision_plan, rule
            )
            self.assertEqual(errors, [])
            return candidate

        validation = {
            "accepted": False,
            "evaluation_valid": True,
            "invalid_reasons": [],
            "rejection_reasons": ["no_stable_improvement"],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work = root / "work.md"
            work.write_text(prompt, encoding="utf-8")
            with patch("run.process_epoch_batch", side_effect=batch_result), patch(
                "run.select_error_group", side_effect=selector_result
            ), patch("run.localize_selector_group", side_effect=localization), patch(
                "run.propose_selector_edit",
                return_value={
                    "schema_version": "prompt-edit-plan-v2",
                    "intent": "Add the selected behavior.",
                    "positive_trigger": (
                        "Represent each explicitly stated performed action as exactly one corresponding activity."
                    ),
                    "negative_boundary": (
                        "Do not turn unstated or non-behavioral context into activities."
                    ),
                    "change_instruction": "Write the canonical rule.",
                },
            ), patch("run.rewrite_prompt", side_effect=rewrite), patch(
                "run.evaluate_gate",
                return_value=([], [], {}, {}, validation),
            ):
                final_prompt, _ = run_training_iterations(
                    args=args,
                    llm_client=object(),
                    train_cases=cases,
                    source_dataset_counts={"bp": len(cases)},
                    run_dir=root,
                    work_prompt_path=work,
                    label="selector-test",
                    validation_cases=cases,
                )
            first_after = (root / "iteration_001" / "prompts" / "after.md").read_text(
                encoding="utf-8"
            )
            second_before = (root / "iteration_002" / "prompts" / "before.md").read_text(
                encoding="utf-8"
            )
            first_decision = json.loads(
                (root / "iteration_001" / "decision" / "acceptance.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(first_after, second_before)
        self.assertTrue(first_decision["applied"])
        self.assertFalse(first_decision["accepted"])
        self.assertEqual(final_prompt.count("Represent each explicitly stated"), 2)

    def test_multi_candidate_attempts_apply_second_and_gate_heldout_on_prompt_change(self):
        prompt = (
            "## agent task\nTask\n\n## input\nInput\n\n"
            "## output\nOutput PlantUML code only.\n\n"
            "## workflow\n(None)\n\n## knowledge\n(None)\n\n## rule\n(None)\n"
        )
        cases = [
            Case(dataset="data", case_id="c1", content="Open database.", gold_plantuml="G"),
            Case(dataset="data", case_id="c2", content="Save database.", gold_plantuml="G"),
        ]

        def run_once(
            decisions,
            max_attempts=3,
            gate2_decisions=None,
            *,
            iterations=1,
            stop_after_first_apply=False,
        ):
            cli_args = [
                    "--iterations",
                    str(iterations),
                    "--analysis-batch-size",
                    "10",
                    "--candidate-application-mode",
                    "cumulative",
                "--max-candidate-attempts-per-epoch",
                str(max_attempts),
            ]
            if gate2_decisions is not None:
                cli_args.append("--gate2")
            if stop_after_first_apply:
                cli_args.append("--stop-after-first-apply")
            args = build_parser().parse_args(cli_args)
            errors = [
                {
                    "finding_id": index,
                    "finding_key": f"finding_key_{index}",
                    "status": "actionable",
                    "primary_finding_id": None,
                    "dataset": "data",
                    "case_id": f"c{index}",
                    "batch_id": 1,
                    "anchor_kind": "missing_node",
                    "error_anchor": f"Action {index}",
                    "matching_quality": "bijective",
                    "requirement_quote": f"Action {index}",
                    "error_summary": f"Action {index} is missing.",
                    "causal_rationale": f"The requirement states action {index}.",
                }
                for index in (1, 2)
            ]

            def batch_result(**kwargs):
                return EpochBatchResult(
                    batch_index=1,
                    global_update_step=1,
                    records=[],
                    summary={},
                    batch_summary={"batch_index": 1},
                    failure_analysis={"schema_version": "failure-errors-v2", "errors": errors},
                    error_observations=errors,
                    valid_pattern_count=2,
                )

            groups = [
                {
                    "local_group_id": f"g{index}",
                    "group_id": f"group_{index}",
                    "finding_ids": [index],
                    "group_summary": f"Action {index} is missing.",
                    "shared_cause": f"The requirement states action {index}.",
                    "members": [errors[index - 1]],
                }
                for index in (1, 2)
            ]

            def selector_result(**kwargs):
                return {
                    "schema_version": "error-selector-v2",
                    "error_groups": groups,
                    "selection_status": "selected",
                    "selected_group_id": "group_1",
                    "selection_rationale": "The groups are priority ordered.",
                    "selected_group": groups[0],
                }

            def localization(**kwargs):
                return {
                    "schema_version": "prompt-gap-localization-v1",
                    "localization_status": "localized",
                    "prompt_gap": "missing",
                    "section": "rule",
                    "operation": "replace_existing",
                    "existing_prompt_quote": "(None)",
                    "rationale": "The rule is absent.",
                }

            def editor(*, selected_group, **kwargs):
                group_id = selected_group["group_id"]
                return {
                    "schema_version": "prompt-edit-plan-v2",
                    "intent": f"Handle {group_id}.",
                    "positive_trigger": f"Apply positive trigger for {group_id}.",
                    "negative_boundary": f"Respect negative boundary for {group_id}.",
                    "change_instruction": "Write the frozen rule.",
                }

            def rewrite(*, current_prompt, revision_plan, output_path, **kwargs):
                item = revision_plan["revision_plan"][0]
                rule = f"{item['positive_trigger']} {item['negative_boundary']}"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json.dumps({"rule_text": rule}), encoding="utf-8")
                return current_prompt.replace("## rule\n(None)", f"## rule\n{rule}")

            decision_iter = iter(decisions)
            gate2_iter = iter(gate2_decisions or [])
            baseline_caches = []
            gate_names = []

            def validation(**kwargs):
                gate_name = kwargs.get("gate_name", "gate1")
                accepted = (
                    next(gate2_iter)
                    if gate_name == "gate2"
                    else next(decision_iter)
                )
                baseline_caches.append(kwargs["baseline_cache"])
                gate_names.append(gate_name)
                return (
                    [],
                    [],
                    {"llm_node_f1": 0.5},
                    {"llm_node_f1": 0.6 if accepted else 0.4},
                    {
                        "accepted": accepted,
                        "evaluation_valid": True,
                        "invalid_reasons": [],
                        "rejection_reasons": (
                            [] if accepted else ["required_metric_not_improved"]
                        ),
                        "candidate_evidence_family": "semantic",
                        "acceptance_policy": "all-required-positive-mean-delta",
                        "gate_sequence_policy": "gate1-then-fresh-gate2",
                        "required_metrics": ["llm_node_f1"],
                        "required_metric_results": {
                            "llm_node_f1": {
                                "available": True,
                                "mean_delta": 0.1 if accepted else -0.1,
                                "positive_mean_delta": accepted,
                            }
                        },
                        "incomplete_required_metrics": [],
                        "non_improving_required_metrics": (
                            [] if accepted else ["llm_node_f1"]
                        ),
                        "direct_metric": None,
                        "direct_metric_results": {},
                        "metric_results": {
                            "llm_node_f1": {
                                "available": True,
                                "mean_delta": 0.1 if accepted else -0.1,
                                "positive_mean_delta": accepted,
                            },
                        },
                    },
                )

            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                work = root / "work.md"
                work.write_text(prompt, encoding="utf-8")
                with patch("run.process_epoch_batch", side_effect=batch_result), patch(
                    "run.select_error_group", side_effect=selector_result
                ), patch("run.localize_selector_group", side_effect=localization), patch(
                    "run.propose_selector_edit", side_effect=editor
                ), patch("run.rewrite_prompt", side_effect=rewrite), patch(
                    "run.evaluate_gate", side_effect=validation
                ) as validation_mock, patch(
                    "run.evaluate_iteration_test", return_value={"llm_node_f1": 0.7}
                ) as heldout_mock:
                    final_prompt, _ = run_training_iterations(
                        args=args,
                        llm_client=object(),
                        train_cases=cases,
                        source_dataset_counts={"bp": len(cases)},
                        run_dir=root,
                        work_prompt_path=work,
                        label="selector-test",
                        validation_cases=cases,
                        confirmation_cases=cases,
                        test_cases=cases,
                        test_dataset="heldout",
                    )
                attempts = json.loads(
                    (root / "iteration_001" / "decision" / "candidate_attempts.json").read_text(
                        encoding="utf-8"
                    )
                )
                acceptance = json.loads(
                    (root / "iteration_001" / "decision" / "acceptance.json").read_text(
                        encoding="utf-8"
                    )
                )
                skip_manifest = root / "iteration_001" / "test" / "manifest.json"
                skip_payload = (
                    json.loads(skip_manifest.read_text(encoding="utf-8"))
                    if skip_manifest.exists()
                    else None
                )
                registry_payload = json.loads(
                    (root / "candidate_registry.json").read_text(encoding="utf-8")
                )
                return {
                    "final_prompt": final_prompt,
                    "attempts": attempts,
                    "acceptance": acceptance,
                    "validation_calls": validation_mock.call_count,
                    "heldout_calls": heldout_mock.call_count,
                    "skip_payload": skip_payload,
                    "baseline_cache_ids": [id(item) for item in baseline_caches],
                    "baseline_caches": baseline_caches,
                    "gate_names": gate_names,
                    "group_attempts": registry_payload["group_attempts"],
                    "iteration_002_exists": (root / "iteration_002").exists(),
                }

        changed = run_once([False, True], gate2_decisions=[True])
        self.assertEqual(changed["validation_calls"], 3)
        self.assertEqual(changed["heldout_calls"], 1)
        self.assertEqual(changed["attempts"]["applied_attempt"], 2)
        self.assertEqual(changed["attempts"]["attempt_count"], 2)
        self.assertEqual(len(changed["group_attempts"]), 2)
        self.assertEqual(
            changed["acceptance"]["acceptance_policy"],
                "all-required-positive-pooled-balanced-and-source-weighted-mean-delta",
        )
        self.assertEqual(
            changed["acceptance"]["gate_sequence_policy"],
            "gate1-then-fresh-gate2",
        )
        self.assertEqual(
            changed["acceptance"]["required_metrics"], ["llm_node_f1"]
        )
        self.assertIn(
            "llm_node_f1", changed["acceptance"]["required_metric_results"]
        )
        self.assertEqual(
            changed["acceptance"]["acceptance_decision"]["metric_results"],
            changed["attempts"]["attempts"][1]["acceptance_decision"][
                "metric_results"
            ],
        )
        screen_caches = [
            cache
            for cache, gate_name in zip(changed["baseline_caches"], changed["gate_names"])
            if gate_name == "gate1"
        ]
        confirmation_caches = [
            cache
            for cache, gate_name in zip(changed["baseline_caches"], changed["gate_names"])
            if gate_name == "gate2"
        ]
        self.assertEqual(len({id(cache) for cache in screen_caches}), 1)
        self.assertEqual(confirmation_caches, [None])
        self.assertIn("group_2", changed["final_prompt"])

        unchanged = run_once([False, False])
        self.assertEqual(unchanged["validation_calls"], 2)
        self.assertEqual(unchanged["heldout_calls"], 0)
        self.assertIsNone(unchanged["attempts"]["applied_attempt"])
        self.assertEqual(unchanged["skip_payload"]["reason"], "prompt_unchanged")
        self.assertEqual(unchanged["final_prompt"], prompt)
        self.assertEqual(len(unchanged["group_attempts"]), 2)

        confirmation_rejected = run_once(
            [True, True], gate2_decisions=[False, True]
        )
        self.assertEqual(confirmation_rejected["validation_calls"], 4)
        self.assertEqual(confirmation_rejected["attempts"]["applied_attempt"], 2)
        self.assertEqual(
            confirmation_rejected["attempts"]["attempts"][0]["rejection_reasons"][0],
            "gate2_rejected",
        )
        self.assertEqual(confirmation_rejected["heldout_calls"], 1)
        self.assertIn("group_2", confirmation_rejected["final_prompt"])

        limited = run_once([False], max_attempts=1)
        self.assertEqual(limited["validation_calls"], 1)
        self.assertEqual(limited["attempts"]["attempt_count"], 1)
        self.assertEqual(len(limited["group_attempts"]), 1)
        self.assertEqual(limited["heldout_calls"], 0)

        stopped = run_once(
            [False, True],
            gate2_decisions=[True],
            iterations=3,
            stop_after_first_apply=True,
        )
        self.assertEqual(stopped["heldout_calls"], 1)
        self.assertFalse(stopped["iteration_002_exists"])

        no_apply = run_once(
            [False, False],
            iterations=2,
            stop_after_first_apply=True,
        )
        self.assertTrue(no_apply["iteration_002_exists"])


if __name__ == "__main__":
    unittest.main()
