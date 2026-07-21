import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ape_datasets.lato import Case
from run import (
    EpochBatchResult,
    build_prompt_gap_consensus,
    build_parser,
    collect_selected_batch_revisions,
    create_selected_batch_revision,
    iteration_paths,
    make_iteration_manifest,
    run_training_iterations,
    write_attribution_lineage,
)


PROMPT = """## agent task

Generate UML activity diagrams.

## input

Read requirements.

## output

Return PlantUML code.

## workflow

Extract explicit actions.

## knowledge

Use fork only for explicit parallel work.

## rule

Do not invent behavior.
"""


def revision_input(batch_id: int, dataset: str, case_ids: list[str]):
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
            "llm_node_f1": 0.7,
            "llm_relation_f1": 0.4,
            "plantuml_compiles": True,
        }
        for case_id in case_ids
    ]
    return {
        "batch_id": batch_id,
        "mechanism_id": "explicit_concurrency_not_mapped",
        "selected_mechanism_signature": signature,
        "supporting_evidence_ids": [item["evidence_id"] for item in evidence],
        "supporting_evidence": evidence,
        "analysis_summary": {},
        "failure_analysis": {},
        "error_localization": {},
        "revision_plan": [
            {
                "section": "knowledge",
                "operation": "qualify_existing",
                "text_to_modify": "Use fork only for explicit parallel work.",
                "intent": "Constrain fork use.",
                "positive_trigger": "Use fork for explicit concurrency.",
                "negative_boundary": "Do not use fork for ordinary lists.",
                "change_instruction": "Tighten the existing fork boundary.",
            }
        ],
    }


def batch_result(batch_index: int, item):
    observation = {
        "batch_id": item["batch_id"],
        "mechanism_id": item["mechanism_id"],
        "mechanism_signature": item["selected_mechanism_signature"],
        "classification": "candidate",
        "candidate_eligible": True,
        "evidence_basis": "requirement_and_gold",
        "pattern_names": ["missing explicit fork"],
        "patterns": [],
        "supporting_evidence_ids": item["supporting_evidence_ids"],
        "supporting_evidence": item["supporting_evidence"],
        "analysis_summary": {},
        "positive_trigger": "Use fork for explicit concurrency.",
        "negative_boundary": "Do not use fork for ordinary lists.",
    }
    return EpochBatchResult(
        batch_index=batch_index,
        global_update_step=batch_index,
        records=[],
        summary={},
        batch_summary={"batch_index": batch_index},
        failure_analysis={"error_patterns": [], "evidence_catalog": item["supporting_evidence"]},
        mechanism_observations=[observation],
        valid_pattern_count=1,
    )


def edit_result(
    item: dict,
    *,
    prompt_gap: str = "missing",
    section: str = "knowledge",
    localization_status: str = "success",
    editor_status: str = "success",
):
    return {
        "batch_id": item["batch_id"],
        "prompt_gap": prompt_gap,
        "target_section": section if prompt_gap != "already_covered" else None,
        "localization_status": localization_status,
        "editor_status": editor_status,
        "revision_input": item if editor_status == "success" else None,
    }


class MechanismTrainingFlowTest(unittest.TestCase):
    def make_args(self):
        return build_parser().parse_args(["--iterations", "1", "--analysis-batch-size", "2"])

    def make_cases(self):
        return [
            Case(dataset="a" if index <= 2 else "b", case_id=f"c-{index}", content="R", gold_plantuml="G")
            for index in range(1, 5)
        ]

    def test_default_taxonomy_is_v3(self):
        self.assertEqual(self.make_args().mechanism_taxonomy_path.name, "mechanism_taxonomy_v3.json")

    def test_attribution_lineage_connects_local_plan_fragment_and_decision(self):
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "mechanism_signature": {"requirement_trigger": "explicit_concurrency"},
            "supporting_attribution_ids": ["attr-1"],
            "supporting_evidence_ids": ["evidence-1"],
        }
        scope = {
            "mechanism_id": selected["mechanism_id"],
            "mechanism_signature": selected["mechanism_signature"],
            "supporting_attribution_ids": ["attr-1"],
            "prompt_gap": "missing",
            "section": "knowledge",
            "repair_type": "construct_selection",
            "existing_prompt_quote": "",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            rewrite_output = root / "rewrite.json"
            rewrite_output.write_text(json.dumps({"rule_text": "narrow rule"}), encoding="utf-8")
            lineage_path = root / "lineage.json"
            write_attribution_lineage(
                path=lineage_path,
                selected_mechanism=selected,
                batch_edit_results=[
                    {
                        "batch_id": 1,
                        "prompt_gap": "missing",
                        "target_section": "knowledge",
                        "editor_status": "success",
                        "revision_input": {
                            "supporting_attribution_ids": ["attr-1"],
                            "revision_scope": scope,
                        },
                    }
                ],
                prompt_gap_audit={"decision": "proceed", "consensus_scope": scope},
                epoch_revision_plan={"revision_scope": scope},
                prompt_rewriter_output_path=rewrite_output,
                acceptance={"accepted": False, "rejection_reasons": ["no_stable_improvement"]},
            )
            lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
        self.assertEqual(lineage["attributions"][0]["attribution_id"], "attr-1")
        self.assertEqual(lineage["attributions"][0]["local_plans"][0]["batch_id"], 1)
        self.assertEqual(lineage["attributions"][0]["final_fragment"]["rule_text"], "narrow rule")
        self.assertFalse(lineage["attributions"][0]["acceptance"]["accepted"])

    def test_no_eligible_cluster_does_not_call_planner(self):
        args = self.make_args()
        item = revision_input(1, "a", ["a-1", "a-2", "a-3"])
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work = root / "work.md"
            work.write_text(PROMPT, encoding="utf-8")
            with patch("run.process_epoch_batch", return_value=batch_result(1, item)), patch("run.plan_epoch_revision") as planner, patch(
                "run.collect_selected_batch_revisions"
            ) as collect:
                run_training_iterations(
                    args=args,
                    llm_client=object(),
                    train_cases=self.make_cases()[:2],
                    run_dir=root,
                    work_prompt_path=work,
                    label="test",
                )
            planner.assert_not_called()
            collect.assert_called_once()
            decision = json.loads((root / "iteration_001" / "decision" / "acceptance.json").read_text(encoding="utf-8"))
            self.assertIn(
                decision["rejection_reasons"],
                [["no_valid_selected_mechanism_plans"], ["insufficient_prompt_gap_consensus"]],
            )

    def test_valid_record_only_patterns_report_no_candidate(self):
        args = self.make_args()
        item = revision_input(1, "a", ["a-1"])
        result = batch_result(1, item)
        result.mechanism_observations[0].update(
            {
                "mechanism_id": None,
                "classification": "record_only",
                "candidate_eligible": False,
            }
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work = root / "work.md"
            work.write_text(PROMPT, encoding="utf-8")
            with patch("run.process_epoch_batch", return_value=result), patch("run.plan_epoch_revision") as planner:
                run_training_iterations(
                    args=args,
                    llm_client=object(),
                    train_cases=self.make_cases()[:2],
                    run_dir=root,
                    work_prompt_path=work,
                    label="test",
                )
            planner.assert_not_called()
            decision = json.loads((root / "iteration_001" / "decision" / "acceptance.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["rejection_reasons"], ["no_candidate_eligible_patterns"])

    def test_selected_mechanism_with_no_valid_local_plans_stops_before_planner(self):
        args = self.make_args()
        items = [
            revision_input(1, "a", ["a-1", "a-2"]),
            revision_input(2, "b", ["b-1"]),
        ]
        results = [batch_result(1, items[0]), batch_result(2, items[1])]
        edit_results = [
            edit_result(item, editor_status="invalid")
            for item in items
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work = root / "work.md"
            work.write_text(PROMPT, encoding="utf-8")
            with patch("run.process_epoch_batch", side_effect=results), patch(
                "run.collect_selected_batch_revisions", return_value=edit_results
            ), patch("run.plan_epoch_revision") as planner:
                run_training_iterations(
                    args=args,
                    llm_client=object(),
                    train_cases=self.make_cases(),
                    run_dir=root,
                    work_prompt_path=work,
                    label="test",
                )
            planner.assert_not_called()
            decision = json.loads((root / "iteration_001" / "decision" / "acceptance.json").read_text(encoding="utf-8"))
            self.assertEqual(decision["rejection_reasons"], ["no_valid_selected_mechanism_plans"])

    def test_collect_selected_revisions_only_edits_supporting_batches(self):
        args = self.make_args()
        items = [
            revision_input(1, "a", ["a-1", "a-2"]),
            revision_input(2, "b", ["b-1"]),
        ]
        observations = [
            batch_result(1, items[0]).mechanism_observations[0],
            batch_result(2, items[1]).mechanism_observations[0],
        ]
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "supporting_batch_observations": observations,
        }
        batch_results = [batch_result(1, items[0]), batch_result(2, items[1]), batch_result(3, revision_input(3, "c", ["c-1"]))]
        first = edit_result(items[0])
        with patch("run.create_selected_batch_revision", side_effect=[first, None]) as create, patch(
            "run.record_unselected_batch"
        ) as mark:
            edit_results = collect_selected_batch_revisions(
                args=args,
                llm_client=object(),
                run_dir=Path("run"),
                iter_dir=Path("iter"),
                prompt=PROMPT,
                batch_results=batch_results,
                selected_mechanism=selected,
                has_accepted_update=False,
                iteration=1,
            )
        self.assertEqual([item["batch_id"] for item in edit_results], [1, 2])
        self.assertEqual(edit_results[1]["prompt_gap"], "invalid")
        self.assertEqual(create.call_count, 2)
        mark.assert_called_once()

    def test_already_covered_localization_skips_editor_without_becoming_invalid(self):
        args = self.make_args()
        selected_observation = {
            "batch_id": 1,
            "mechanism_id": "explicit_concurrency_not_mapped",
            "mechanism_signature": revision_input(1, "a", ["a-1"])["selected_mechanism_signature"],
            "supporting_evidence_ids": ["run:i001:b001:a:a-1"],
            "positive_trigger": "Use fork for explicit concurrency.",
            "negative_boundary": "Do not use fork for ordinary lists.",
            "supporting_evidence": [],
            "analysis_summary": {},
            "patterns": [],
        }
        covered = {
            "prompt_gap": "already_covered",
            "existing_prompt_quote": "Use fork only for explicit parallel work.",
            "gap_rationale": "The current prompt already states the selected boundary.",
            "section_diagnoses": [],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            iter_dir = root / "iteration_001"
            batch_dir = iter_dir / "train_batches" / "batch_001"
            paths = iteration_paths(batch_dir)
            batch_dir.mkdir(parents=True)
            paths["manifest"].write_text(
                json.dumps(make_iteration_manifest(batch_dir, 1, paths)),
                encoding="utf-8",
            )
            with patch(
                "run.sanitize_selected_failure_analysis",
                return_value={"error_patterns": [{"name": "x"}], "evidence_catalog": []},
            ), patch("run.localize_errors", return_value=covered), patch(
                "run.propose_prompt_revision"
            ) as editor:
                result = create_selected_batch_revision(
                    args=args,
                    llm_client=object(),
                    run_dir=root,
                    iter_dir=iter_dir,
                    prompt=PROMPT,
                    selected_observation=selected_observation,
                    has_accepted_update=False,
                    iteration=1,
                )
            editor.assert_not_called()
            self.assertEqual(result["prompt_gap"], "already_covered")
            self.assertEqual(result["editor_status"], "skipped")
            manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
            self.assertEqual(manifest["stages"]["selected_mechanism_editing"]["status"], "skipped")

    def test_empty_sanitized_evidence_stops_before_localization(self):
        args = self.make_args()
        selected_observation = {
            "batch_id": 1,
            "mechanism_id": "explicit_concurrency_not_mapped",
            "mechanism_signature": {},
            "supporting_evidence_ids": ["e1"],
            "positive_trigger": "Use fork for explicit concurrency.",
            "negative_boundary": "Do not use fork for ordinary lists.",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            iter_dir = root / "iteration_001"
            batch_dir = iter_dir / "train_batches" / "batch_001"
            paths = iteration_paths(batch_dir)
            batch_dir.mkdir(parents=True)
            paths["manifest"].write_text(
                json.dumps(make_iteration_manifest(batch_dir, 1, paths)),
                encoding="utf-8",
            )
            with patch(
                "run.sanitize_selected_failure_analysis",
                return_value={"error_patterns": [], "evidence_catalog": []},
            ), patch("run.localize_errors") as localizer, patch("run.propose_prompt_revision") as editor:
                result = create_selected_batch_revision(
                    args=args,
                    llm_client=object(),
                    run_dir=root,
                    iter_dir=iter_dir,
                    prompt=PROMPT,
                    selected_observation=selected_observation,
                    has_accepted_update=False,
                    iteration=1,
                )
            localizer.assert_not_called()
            editor.assert_not_called()
            self.assertEqual(result["prompt_gap"], "invalid")
            manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
            self.assertIn(
                "selected_evidence_empty_after_sanitization",
                manifest["stages"]["selected_mechanism_editing"]["note"],
            )

    def run_gate_result(self, accepted: bool) -> tuple[str, dict]:
        args = self.make_args()
        items = [
            revision_input(1, "a", ["a-1", "a-2"]),
            revision_input(2, "b", ["b-1"]),
        ]
        results = [batch_result(1, items[0]), batch_result(2, items[1])]
        candidate = PROMPT.replace(
            "Use fork only for explicit parallel work.",
            "Use fork only for explicitly concurrent work.",
        )
        planner_output = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "selected_mechanism_signature": items[0]["selected_mechanism_signature"],
            "supporting_evidence_ids": ["run:i001:b001:a:a-1", "run:i001:b001:a:a-2", "run:i001:b002:b:b-1"],
            "revision_plan": items[0]["revision_plan"],
        }
        decision = {
            "accepted": accepted,
            "acceptance_mode": "any_improvement" if accepted else "rejected",
            "acceptance_policy": "any-improvement",
            "rejection_reasons": [] if accepted else ["no_stable_improvement"],
            "winning_metrics": ["llm_node_f1"] if accepted else [],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            work = root / "work.md"
            work.write_text(PROMPT, encoding="utf-8")
            with patch("run.process_epoch_batch", side_effect=results), patch(
                "run.collect_selected_batch_revisions",
                return_value=[edit_result(item) for item in items],
            ), patch("run.plan_epoch_revision", return_value=planner_output), patch(
                "run.rewrite_prompt", return_value=candidate
            ), patch(
                "run.evaluate_validation_gate",
                return_value=([], [], {}, {}, decision),
            ):
                run_training_iterations(
                    args=args,
                    llm_client=object(),
                    train_cases=self.make_cases(),
                    run_dir=root,
                    work_prompt_path=work,
                    label="test",
                    validation_cases=self.make_cases()[:2],
                )
            final_prompt = work.read_text(encoding="utf-8")
            saved_decision = json.loads((root / "iteration_001" / "decision" / "acceptance.json").read_text(encoding="utf-8"))
            consensus = json.loads(
                (root / "iteration_001" / "mechanisms" / "prompt_gap_consensus.json").read_text(encoding="utf-8")
            )
            self.assertEqual(consensus["decision"], "proceed")
            self.assertEqual(consensus["required_votes"], 2)
            return final_prompt, saved_decision

    def test_prompt_gap_consensus_uses_strict_majority(self):
        items = [
            revision_input(1, "a", ["a-1"]),
            revision_input(2, "b", ["b-1"]),
            revision_input(3, "c", ["c-1"]),
            revision_input(4, "d", ["d-1"]),
        ]

        def selected(count: int):
            return {
                "mechanism_id": "explicit_concurrency_not_mapped",
                "supporting_batch_count": count,
                "supporting_batches": list(range(1, count + 1)),
            }

        cases = [
            (2, 2, True),
            (3, 2, True),
            (4, 3, True),
            (2, 1, False),
            (3, 1, False),
            (4, 2, False),
        ]
        for batch_count, positive_count, should_proceed in cases:
            with self.subTest(batch_count=batch_count, positive_count=positive_count):
                results = [
                    edit_result(items[index])
                    if index < positive_count
                    else edit_result(items[index], prompt_gap="already_covered", editor_status="skipped")
                    for index in range(batch_count)
                ]
                revisions, audit, reason = build_prompt_gap_consensus(
                    selected_mechanism=selected(batch_count),
                    batch_edit_results=results,
                )
                self.assertEqual(audit["decision"] == "proceed", should_proceed)
                self.assertEqual(bool(revisions), should_proceed)
                self.assertEqual(reason is None, should_proceed)

    def test_prompt_gap_consensus_keeps_invalid_in_denominator_and_requires_one_section(self):
        items = [
            revision_input(1, "a", ["a-1"]),
            revision_input(2, "b", ["b-1"]),
            revision_input(3, "c", ["c-1"]),
        ]
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "supporting_batch_count": 3,
            "supporting_batches": [1, 2, 3],
        }
        results = [
            edit_result(items[0], section="workflow"),
            edit_result(items[1], section="knowledge"),
            edit_result(
                items[2],
                prompt_gap="invalid",
                section=None,
                localization_status="invalid",
                editor_status="not_run",
            ),
        ]
        revisions, audit, reason = build_prompt_gap_consensus(
            selected_mechanism=selected,
            batch_edit_results=results,
        )
        self.assertEqual(revisions, [])
        self.assertEqual(audit["required_votes"], 2)
        self.assertEqual(reason, "insufficient_prompt_gap_consensus")

    def test_prompt_gap_consensus_requires_complete_scope_not_section_only(self):
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "mechanism_signature": revision_input(1, "a", ["a-1"])["selected_mechanism_signature"],
            "supporting_attribution_ids": ["attr-1"],
            "supporting_batch_count": 2,
            "supporting_batches": [1, 2],
        }
        scope_one = {
            "mechanism_id": selected["mechanism_id"],
            "mechanism_signature": selected["mechanism_signature"],
            "supporting_attribution_ids": ["attr-1"],
            "prompt_gap": "missing",
            "section": "knowledge",
            "repair_type": "construct_selection",
            "existing_prompt_quote": "",
        }
        scope_two = {**scope_one, "repair_type": "relation_grounding"}
        results = [
            {
                "batch_id": 1,
                "prompt_gap": "missing",
                "target_section": "knowledge",
                "localization_status": "success",
                "editor_status": "success",
                "revision_scope": scope_one,
                "revision_input": {"revision_scope": scope_one},
            },
            {
                "batch_id": 2,
                "prompt_gap": "missing",
                "target_section": "knowledge",
                "localization_status": "success",
                "editor_status": "success",
                "revision_scope": scope_two,
                "revision_input": {"revision_scope": scope_two},
            },
        ]
        revisions, audit, reason = build_prompt_gap_consensus(
            selected_mechanism=selected,
            batch_edit_results=results,
        )
        self.assertEqual(revisions, [])
        self.assertEqual(audit["decision"], "insufficient_consensus")
        self.assertEqual(reason, "insufficient_prompt_gap_consensus")

    def test_prompt_gap_consensus_is_independent_of_batch_completion_order(self):
        items = [
            revision_input(1, "a", ["a-1"]),
            revision_input(2, "b", ["b-1"]),
            revision_input(3, "c", ["c-1"]),
        ]
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "supporting_batch_count": 3,
            "supporting_batches": [1, 2, 3],
        }
        results = [
            edit_result(items[0]),
            edit_result(items[1]),
            edit_result(items[2], prompt_gap="already_covered", editor_status="skipped"),
        ]
        forward = build_prompt_gap_consensus(
            selected_mechanism=selected,
            batch_edit_results=results,
        )
        reversed_result = build_prompt_gap_consensus(
            selected_mechanism=selected,
            batch_edit_results=list(reversed(results)),
        )
        self.assertEqual(forward, reversed_result)

    def test_all_covered_is_a_distinct_abstention(self):
        items = [revision_input(1, "a", ["a-1"]), revision_input(2, "b", ["b-1"])]
        selected = {
            "mechanism_id": "explicit_concurrency_not_mapped",
            "supporting_batch_count": 2,
            "supporting_batches": [1, 2],
        }
        results = [
            edit_result(item, prompt_gap="already_covered", editor_status="skipped")
            for item in items
        ]
        revisions, audit, reason = build_prompt_gap_consensus(
            selected_mechanism=selected,
            batch_edit_results=results,
        )
        self.assertEqual(revisions, [])
        self.assertEqual(audit["decision"], "already_covered")
        self.assertEqual(reason, "selected_mechanism_already_covered")

    def test_accepted_gate_updates_work_prompt(self):
        final_prompt, decision = self.run_gate_result(True)
        self.assertIn("explicitly concurrent work", final_prompt)
        self.assertTrue(decision["accepted"])
        self.assertEqual(decision["mechanism_taxonomy_version"], "v3")

    def test_rejected_gate_keeps_work_prompt(self):
        final_prompt, decision = self.run_gate_result(False)
        self.assertEqual(final_prompt, PROMPT)
        self.assertFalse(decision["accepted"])


if __name__ == "__main__":
    unittest.main()
