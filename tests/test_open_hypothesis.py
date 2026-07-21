import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from analysis.mechanism_clustering import (
    build_mechanism_observations,
    load_mechanism_taxonomy,
    select_epoch_mechanism,
    validate_failure_analysis_payload,
)
from analysis.mechanism_memory import (
    active_memory_entries,
    load_memory,
    mark_hypothesis_status,
    record_observations,
    save_memory,
)
from analysis.prompt_rewriter import rewrite_prompt
from run import build_prompt_gap_consensus


PROJECT_DIR = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = PROJECT_DIR / "prompt_workspace" / "mechanism_taxonomy_v3.json"


def evidence(**overrides):
    item = {
        "evidence_id": "run:i001:b001:data:case-1",
        "dataset": "data",
        "case_id": "case-1",
        "requirement": "Task A and Task B run concurrently.",
        "llm_missing_nodes": [],
        "llm_extra_nodes": [],
        "llm_missing_relations": ["Task A -> Task B (fork)"],
        "llm_extra_relations": [],
        "syntax_errors": [],
        "compile_errors": [],
        "syntax_passed": True,
        "plantuml_compiles": True,
        "matching_quality": {"status": "valid", "reasons": []},
        "llm_node_f1": 1.0,
        "llm_relation_f1": 0.2,
    }
    item.update(overrides)
    return item


def attribution(**overrides):
    item = {
        "evidence_id": "run:i001:b001:data:case-1",
        "role": "primary",
        "requirement_quote": "Task A and Task B run concurrently",
        "error_anchor": "Task A -> Task B (fork)",
        "failure_direction": "missing_required_parallel",
        "construct_family": "fork",
        "requirement_trigger": "explicit_concurrency",
        "gold_state": "absent",
        "prediction_state": "absent",
        "node_inventory_status": "sufficient",
        "evidence_basis": "requirement_and_gold",
        "causal_rationale": "The exact concurrency relation is missing.",
    }
    item.update(overrides)
    return item


def atomic_payload(*items):
    return {"schema_version": "atomic-v1", "error_attributions": list(items)}


class OpenHypothesisTest(unittest.TestCase):
    def setUp(self):
        self.taxonomy = load_mechanism_taxonomy(TAXONOMY_PATH)

    def test_single_primary_attribution_creates_dynamic_candidate(self):
        result = validate_failure_analysis_payload(
            atomic_payload(attribution()),
            evidence_catalog=[evidence()],
        )
        self.assertIsNotNone(result.normalized_payload)
        observations = build_mechanism_observations(
            result.normalized_payload,
            self.taxonomy,
            batch_id=1,
            analysis_summary={},
        )
        self.assertEqual(len(observations), 1)
        self.assertTrue(observations[0]["candidate_eligible"])
        self.assertTrue(observations[0]["mechanism_id"].startswith("hyp_"))
        selected, report = select_epoch_mechanism(observations)
        self.assertIsNotNone(selected)
        self.assertEqual(report["selected_hypothesis_id"], selected["hypothesis_id"])

    def test_action_phrase_cannot_be_primary_environment_context(self):
        catalog = evidence(
            requirement="Open Web application.",
            llm_missing_relations=[],
            llm_extra_nodes=["Open Web application"],
        )
        item = {
            **attribution(),
            "requirement_quote": "Open Web application",
            "error_anchor": "Open Web application",
            "failure_direction": "activity_over_decomposition",
            "construct_family": "activity",
            "requirement_trigger": "environment_context",
            "gold_state": "none",
            "prediction_state": "single",
            "node_inventory_status": "not_applicable",
        }
        result = validate_failure_analysis_payload(
            atomic_payload(item),
            evidence_catalog=[catalog],
        )
        self.assertIsNone(result.normalized_payload)
        self.assertIn("invalid_trigger_grounding", result.rejected_patterns[0]["rejection_reasons"])

    def test_conflicting_direction_blocks_child_hypothesis(self):
        first = {
            "batch_id": 1,
            "mechanism_id": "h1",
            "hypothesis_id": "h1",
            "mechanism_signature": {
                "failure_direction": "missing_required_parallel",
                "construct_family": "fork",
                "requirement_trigger": "explicit_concurrency",
                "gold_state": "present",
                "prediction_state": "absent",
                "node_inventory_status": "sufficient",
            },
            "candidate_eligible": True,
            "evidence_basis": "requirement_and_gold",
            "supporting_attribution_ids": ["a1"],
            "supporting_evidence_ids": ["e1"],
            "supporting_evidence": [{"evidence_id": "e1", "dataset": "d", "case_id": "c1", "llm_relation_f1": 0.2}],
            "attributions": [{"attribution_id": "a1", "role": "primary"}],
            "positive_trigger": "Use fork for explicit concurrency.",
            "negative_boundary": "Do not infer fork without concurrency.",
        }
        opposite = json.loads(json.dumps(first))
        opposite["batch_id"] = 2
        opposite["mechanism_id"] = None
        opposite["hypothesis_id"] = None
        opposite["evidence_basis"] = "requirement_and_gold"
        opposite["mechanism_signature"]["gold_state"] = "absent"
        opposite["mechanism_signature"]["prediction_state"] = "present"
        opposite["supporting_attribution_ids"] = ["a2"]
        opposite["supporting_evidence_ids"] = ["e2"]
        opposite["supporting_evidence"] = [{"evidence_id": "e2", "dataset": "d", "case_id": "c2", "llm_relation_f1": 0.2}]
        opposite["attributions"] = [{"attribution_id": "a2", "role": "primary"}]
        selected, report = select_epoch_mechanism([first, opposite])
        self.assertIsNone(selected)
        self.assertIn("scope_conflict", report["rejected_clusters"][0]["rejection_reasons"])

    def test_memory_deduplicates_and_invalidates_on_prompt_change(self):
        observation = {
            "batch_id": 1,
            "hypothesis_id": "h1",
            "mechanism_id": "h1",
            "parent_key": ["p"],
            "child_key": ["c"],
            "mechanism_signature": {"requirement_trigger": "explicit_concurrency"},
            "candidate_eligible": True,
            "supporting_evidence": [evidence()],
            "evidence_catalog": [evidence()],
            "attributions": [
                {
                    **attribution(),
                    "attribution_id": "a1",
                    "matching_quality": "bijective",
                    "anchor_kind": "missing_relation",
                }
            ],
        }
        memory = load_memory(Path("missing-memory.json"))
        record_observations(memory, [observation], prompt_hash="p1", taxonomy_version="v3", iteration=1)
        record_observations(memory, [observation], prompt_hash="p1", taxonomy_version="v3", iteration=1)
        self.assertEqual(len(memory["entries"]), 1)
        self.assertEqual(len(active_memory_entries(memory, prompt_hash="p1", taxonomy_version="v3")), 1)
        mark_hypothesis_status(memory, prompt_hash="p1", hypothesis_id="h1", status="rejected", rejection_reasons=["validation_gate_rejected"])
        self.assertEqual(active_memory_entries(memory, prompt_hash="p1", taxonomy_version="v3"), [])
        record_observations(memory, [observation], prompt_hash="p2", taxonomy_version="v3", iteration=2)
        self.assertEqual(memory["entries"][0]["status"], "historical")
        self.assertEqual(len(active_memory_entries(memory, prompt_hash="p2", taxonomy_version="v3")), 1)

    def test_single_batch_prompt_gap_vote_is_valid(self):
        selected = {
            "mechanism_id": "h1",
            "mechanism_signature": {"requirement_trigger": "explicit_concurrency"},
            "supporting_attribution_ids": ["a1"],
            "supporting_batch_count": 1,
            "supporting_batches": [1],
        }
        scope = {
            "mechanism_id": "h1",
            "mechanism_signature": selected["mechanism_signature"],
            "supporting_attribution_ids": ["a1"],
            "prompt_gap": "missing",
            "section": "knowledge",
            "repair_type": "construct_selection",
            "existing_prompt_quote": "",
        }
        revisions, audit, reason = build_prompt_gap_consensus(
            selected_mechanism=selected,
            batch_edit_results=[
                {
                    "batch_id": 1,
                    "prompt_gap": "missing",
                    "target_section": "knowledge",
                    "localization_status": "success",
                    "editor_status": "success",
                    "revision_scope": scope,
                    "revision_input": {"revision_scope": scope, "batch_id": 1},
                }
            ],
        )
        self.assertIsNone(reason)
        self.assertEqual(audit["required_votes"], 1)
        self.assertEqual(audit["decision"], "proceed")
        self.assertEqual(len(revisions), 1)

    def test_rewriter_rejects_fields_other_than_rule_text(self):
        prompt = """## agent task

Generate diagrams.

## input

Read requirements.

## output

Return PlantUML code.

## workflow

Extract actions.

## knowledge

Use explicit evidence.

## rule

Do not invent behavior.
"""
        positive = "Use fork for explicit concurrency."
        negative = "Do not infer fork without explicit concurrency."
        revision_plan = {
            "revision_plan": [
                {
                    "section": "knowledge",
                    "operation": "append_new",
                    "text_to_modify": "",
                    "intent": "Add one narrow rule.",
                    "change_instruction": "Append the frozen rule.",
                    "positive_trigger": positive,
                    "negative_boundary": negative,
                }
            ]
        }

        class Client:
            def chat(self, messages, **kwargs):
                return json.dumps(
                    {
                        "rule_text": f"{positive} {negative}",
                        "full_prompt": prompt,
                    }
                )

        args = SimpleNamespace(
            prompt_rewriter_prompt_path=PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_v3.md",
            editor_temperature=0.0,
            editor_max_tokens=256,
            editor_thinking="disabled",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = rewrite_prompt(
                current_prompt=prompt,
                revision_plan=revision_plan,
                args=args,
                llm_client=Client(),
                output_input_path=root / "input.json",
                output_path=root / "output.json",
                state_dir=root,
                iteration=1,
            )
            self.assertIsNone(result)
            self.assertTrue((root / "output.rejected.txt").exists())


if __name__ == "__main__":
    unittest.main()
