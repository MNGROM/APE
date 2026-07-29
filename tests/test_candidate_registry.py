import tempfile
import unittest
from pathlib import Path

from analysis.candidate_registry import (
    evaluated_candidate_ids,
    group_attempt_history,
    group_attempt_signature,
    load_candidate_registry,
    record_evaluated_candidate,
    record_group_attempt,
    save_candidate_registry,
)


class CandidateRegistryTest(unittest.TestCase):
    def test_missing_registry_starts_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate_registry.json"
            loaded = load_candidate_registry(path)
        self.assertEqual(
            loaded,
            {
                "version": "candidate-registry-v1",
                "entries": [],
                "group_attempts": [],
            },
        )

    def test_registry_round_trip_and_blocks_same_base_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate_registry.json"
            registry = load_candidate_registry(path)
            metadata = {
                "candidate_id": "cand_1",
                "group_id": "group_1",
                "finding_ids": [1],
                "finding_keys": ["finding_key_1"],
                "positive_trigger": "Apply the positive side.",
                "negative_boundary": "Exclude the boundary side.",
            }

            record_evaluated_candidate(
                registry,
                iteration=1,
                base_prompt_hash="base_hash",
                candidate_prompt="candidate prompt",
                rule_text="one rule fragment",
                candidate_metadata=metadata,
                validation_diagnostics={"diagnostic_only": True},
                artifact_paths={"candidate_prompt": "iteration_001/prompts/candidate.md"},
            )
            save_candidate_registry(path, registry)
            loaded = load_candidate_registry(path)

            self.assertEqual(
                evaluated_candidate_ids(loaded, base_prompt_hash="base_hash"),
                {"cand_1"},
            )
            self.assertEqual(
                evaluated_candidate_ids(loaded, base_prompt_hash="other_hash"),
                set(),
            )
            self.assertEqual(loaded["entries"][0]["group_id"], "group_1")

    def test_registry_rejects_duplicate_candidate_for_same_base(self) -> None:
        registry = {
            "version": "candidate-registry-v1",
            "entries": [],
            "group_attempts": [],
        }
        kwargs = {
            "iteration": 1,
            "base_prompt_hash": "base_hash",
            "candidate_prompt": "candidate prompt",
            "rule_text": "fragment",
            "candidate_metadata": {
                "candidate_id": "cand_1",
                "group_id": "group_1",
            },
            "validation_diagnostics": {},
            "artifact_paths": {},
        }
        record_evaluated_candidate(registry, **kwargs)

        with self.assertRaisesRegex(ValueError, "already recorded"):
            record_evaluated_candidate(registry, **kwargs)

    def test_group_attempt_history_is_exact_and_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate_registry.json"
            registry = load_candidate_registry(path)
            record_group_attempt(
                registry,
                iteration=2,
                attempt=1,
                base_prompt_hash="base_hash",
                group_id="group_1",
                finding_keys=["finding_b", "finding_a", "finding_a"],
                outcome="already_covered",
                rejection_reasons=["already_covered"],
            )
            save_candidate_registry(path, registry)
            loaded = load_candidate_registry(path)

        history = group_attempt_history(
            loaded,
            base_prompt_hash="base_hash",
            finding_keys=["finding_a", "finding_b"],
        )
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["finding_keys"], ["finding_a", "finding_b"])
        self.assertEqual(history[0]["outcome"], "already_covered")
        self.assertEqual(
            history[0]["group_signature"],
            group_attempt_signature(
                base_prompt_hash="base_hash",
                finding_keys=["finding_b", "finding_a"],
            ),
        )
        self.assertEqual(
            group_attempt_history(
                loaded,
                base_prompt_hash="different_base",
                finding_keys=["finding_a", "finding_b"],
            ),
            [],
        )

    def test_group_attempt_replaces_same_iteration_attempt_record(self) -> None:
        registry = {
            "version": "candidate-registry-v1",
            "entries": [],
            "group_attempts": [],
        }
        kwargs = {
            "iteration": 3,
            "attempt": 2,
            "base_prompt_hash": "base_hash",
            "group_id": "group_1",
            "finding_keys": ["finding_a"],
            "rejection_reasons": [],
        }
        record_group_attempt(registry, outcome="not_generated", **kwargs)
        record_group_attempt(registry, outcome="no_prompt_gap", **kwargs)

        self.assertEqual(len(registry["group_attempts"]), 1)
        self.assertEqual(registry["group_attempts"][0]["outcome"], "no_prompt_gap")


if __name__ == "__main__":
    unittest.main()
