import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ANALYZER_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "analyze_cross_dataset_transfer.py"
)
SPEC = importlib.util.spec_from_file_location(
    "tracked_cross_dataset_transfer_analyzer", ANALYZER_PATH
)
assert SPEC is not None and SPEC.loader is not None
ANALYZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYZER)


DATASET_DELTAS = {
    "bp": (0.015572222222222246, 0.039811111111111054),
    "fsd": (-0.014155555555555513, -0.02427777777777777),
    "pure": (-0.024505555555555596, -0.022527777777777775),
    "rac": (0.060922222222222246, 0.07104999999999999),
    "us": (-0.010577777777777797, 0.018522222222222256),
}


def per_dataset_payload(deltas=DATASET_DELTAS):
    return {
        dataset: {
            "case_count": 6,
            "repeat_count": 3,
            "metrics": {
                "llm_node_f1": {"mean_delta": node},
                "llm_relation_f1": {"mean_delta": relation},
                "plantuml_compilation_pass_rate": {"mean_delta": 0.0},
            },
        }
        for dataset, (node, relation) in deltas.items()
    }


def gate_decision(node, relation, per_dataset, *, accepted=True):
    return {
        "accepted": accepted,
        "evaluation_valid": True,
        "metric_results": {
            "llm_node_f1": {"available": True, "mean_delta": node},
            "llm_relation_f1": {"available": True, "mean_delta": relation},
            "plantuml_compilation_pass_rate": {
                "available": True,
                "mean_delta": 0.0,
            },
        },
        "per_dataset_metric_results": per_dataset,
    }


class CrossDatasetTransferAnalyzerTest(unittest.TestCase):
    def make_run(self, root: Path, *, include_train_cases: bool = True) -> Path:
        run_dir = root / "2026-08-05__17-08-13__test-lmc"
        for attempt, members in {
            1: [
                {
                    "dataset": "bp",
                    "case_id": "bp-0001",
                    "anchor_kind": "extra_node",
                }
            ],
            2: [
                {
                    "dataset": "fsd",
                    "case_id": "fsd-0002",
                    "anchor_kind": "extra_node",
                },
                {
                    "dataset": "fsd",
                    "case_id": "fsd-0002",
                    "anchor_kind": "extra_relation",
                },
            ],
        }.items():
            selected_group = (
                run_dir
                / "iteration_001"
                / "candidate_attempts"
                / f"attempt_{attempt:03d}"
                / "mechanisms"
                / "selected_error_group.json"
            )
            selected_group.parent.mkdir(parents=True)
            selected_group.write_text(
                json.dumps({"members": members}), encoding="utf-8"
            )
        initial_test = run_dir / "iteration_000" / "test"
        final_test = run_dir / "iteration_001" / "test"
        initial_test.mkdir(parents=True)
        final_test.mkdir(parents=True)
        (initial_test / "summary.json").write_text(
            json.dumps(
                {
                    "llm_node_f1": 0.8293,
                    "llm_relation_f1": 0.6493,
                    "plantuml_compilation_pass_rate": 1.0,
                    "infrastructure_error_rate": 0.0,
                }
            ),
            encoding="utf-8",
        )
        (final_test / "summary.json").write_text(
            json.dumps(
                {
                    "llm_node_f1": 0.8632,
                    "llm_relation_f1": 0.7277,
                    "plantuml_compilation_pass_rate": 1.0,
                    "infrastructure_error_rate": 0.0,
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "run_args.json").write_text(
            json.dumps(
                {
                    "test_dataset": "lmc",
                    "llm_provider": "deepseek",
                    "generation_model": "deepseek-v4-flash",
                    "agent_model": "deepseek-v4-flash",
                    "judge_model": "deepseek-v4-flash",
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "data_split_summary.json").write_text(
            json.dumps(
                {
                    "train_dataset_counts": {
                        "bp": 18,
                        "fsd": 104,
                        "pure": 88,
                        "rac": 8,
                        "us": 208,
                    }
                }
            ),
            encoding="utf-8",
        )
        per_dataset = per_dataset_payload()
        registry = {
            "entries": [
                {
                    "candidate_id": "cand_rejected",
                    "iteration": 1,
                    "base_prompt_hash": "base",
                    "candidate_prompt_hash": "rejected",
                    "validation_diagnostics": {
                        "gate1_decision": gate_decision(
                            0.01, 0.02, per_dataset
                        ),
                        "gate2_decision": gate_decision(
                            -0.01, 0.03, per_dataset, accepted=False
                        ),
                    },
                    "artifacts": {
                        "candidate_prompt": (
                            "iteration_001/candidate_attempts/attempt_001/"
                            "prompts/candidate.md"
                        )
                    },
                },
                {
                    "candidate_id": "cand_applied",
                    "iteration": 1,
                    "base_prompt_hash": "base",
                    "candidate_prompt_hash": "candidate",
                    "validation_diagnostics": {
                        "gate1_decision": gate_decision(
                            0.02280666666666668,
                            0.00048666666666670927,
                            per_dataset,
                        ),
                        "gate2_decision": gate_decision(
                            0.005451111111111111,
                            0.01651555555555558,
                            per_dataset,
                        ),
                    },
                    "artifacts": {
                        "candidate_prompt": (
                            "iteration_001/candidate_attempts/attempt_002/"
                            "prompts/candidate.md"
                        )
                    },
                }
            ],
            "group_attempts": [
                {
                    "iteration": 1,
                    "attempt": 1,
                    "candidate_id": "cand_rejected",
                    "outcome": "gate2_rejected",
                },
                {
                    "iteration": 1,
                    "attempt": 2,
                    "candidate_id": "cand_applied",
                    "outcome": "applied",
                },
            ],
        }
        (run_dir / "candidate_registry.json").write_text(
            json.dumps(registry), encoding="utf-8"
        )
        if include_train_cases:
            (run_dir / "train_cases.json").write_text(
                json.dumps(
                    [
                        {"dataset": "bp", "case_id": "bp-0001"},
                        {"dataset": "fsd", "case_id": "fsd-0002"},
                        {"dataset": "fsd", "case_id": "fsd-0003"},
                        {"dataset": "us", "case_id": "us-0001"},
                    ]
                ),
                encoding="utf-8",
            )
        evidence_inventory = run_dir / "iteration_001" / "mechanisms" / "evidence_inventory.json"
        evidence_inventory.parent.mkdir(parents=True, exist_ok=True)
        evidence_inventory.write_text(
            json.dumps(
                [
                    {"dataset": "bp", "status": "actionable"},
                    {"dataset": "fsd", "status": "actionable"},
                    {"dataset": "pure", "status": "secondary"},
                ]
            ),
            encoding="utf-8",
        )
        (run_dir / "rate_limit_events.jsonl").write_text(
            json.dumps({"wait_seconds": 32}) + "\n", encoding="utf-8"
        )
        return run_dir

    def make_glm_run(self, root: Path) -> Path:
        deepseek_run = self.make_run(root)
        run_dir = root / "2026-08-05__19-50-25__test-lmc"
        deepseek_run.rename(run_dir)
        run_args_path = run_dir / "run_args.json"
        run_args = json.loads(run_args_path.read_text(encoding="utf-8"))
        run_args.update(
            {
                "llm_provider": "zhipu",
                "generation_model": "glm-4.7",
                "agent_model": "glm-5.2",
                "judge_model": "glm-5.2",
            }
        )
        run_args_path.write_text(json.dumps(run_args), encoding="utf-8")

        registry_path = run_dir / "candidate_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entry = registry["entries"][0]
        entry["candidate_id"] = "cand_glm_node_only"
        entry["candidate_prompt_hash"] = "glm-candidate"
        entry["validation_diagnostics"] = {
            "gate1_decision": gate_decision(0.012, 0.031, per_dataset_payload()),
            "gate2_decision": gate_decision(-0.023, 0.041, per_dataset_payload()),
        }
        registry["entries"] = [entry]
        registry["group_attempts"] = [
            {
                "iteration": 1,
                "attempt": 1,
                "candidate_id": "cand_glm_node_only",
                "outcome": "applied",
            }
        ]
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        return run_dir

    def test_analyzes_source_macro_weighted_and_heldout_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run(Path(temp_dir))
            before = {
                path.relative_to(run_dir): path.read_bytes()
                for path in run_dir.rglob("*")
                if path.is_file()
            }

            analysis = ANALYZER.analyze_run(run_dir)

            after = {
                path.relative_to(run_dir): path.read_bytes()
                for path in run_dir.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)
            self.assertEqual(analysis["candidate_funnel"]["gate2_rejected"], 1)
            self.assertEqual(len(analysis["evaluated_candidates"]), 2)
            self.assertEqual(len(analysis["applied_candidates"]), 1)
            candidate = analysis["applied_candidates"][0]
            self.assertEqual(
                candidate["source_cases"],
                [{"dataset": "fsd", "case_id": "fsd-0002"}],
            )
            gate2_node = candidate["gate2"]["metrics"]["llm_node_f1"]
            self.assertAlmostEqual(gate2_node["macro_mean_delta"], 0.0054511111)
            self.assertAlmostEqual(
                gate2_node["training_pool_weighted"]["mean_delta"],
                -0.011880672926447578,
            )
            self.assertEqual(
                gate2_node["dataset_effects"]["improved"], ["bp", "rac"]
            )
            self.assertEqual(
                gate2_node["dataset_effects"]["regressed"],
                ["fsd", "pure", "us"],
            )
            self.assertAlmostEqual(
                candidate["heldout"]["metric_deltas"]["llm_node_f1"], 0.0339
            )
            self.assertTrue(candidate["analysis_valid"])
            self.assertEqual(
                candidate["required_metrics"],
                ["llm_node_f1", "llm_relation_f1"],
            )
            self.assertTrue(candidate["gate1"]["counterfactual"]["accepted"])
            self.assertTrue(candidate["gate2"]["counterfactual"]["accepted"])
            self.assertEqual(
                analysis["evidence_funnel"]["discovery_cases"]["datasets"]["fsd"],
                {"count": 2, "share": 0.5},
            )
            self.assertTrue(
                analysis["evidence_funnel"]["discovery_cases"]["available"]
            )
            self.assertEqual(
                analysis["evidence_funnel"]["actionable_findings"]["datasets"]["bp"]["count"],
                1,
            )
            self.assertEqual(
                analysis["evidence_funnel"]["attempt_source_cases"]["datasets"]["fsd"]["count"],
                1,
            )
            self.assertEqual(analysis["retry_summary"]["event_count"], 1)
            self.assertEqual(analysis["retry_summary"]["wait_seconds"], 32.0)
            self.assertEqual(analysis["warnings"], [])

    def test_missing_evidence_artifact_is_unavailable_not_zero(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run(
                Path(temp_dir), include_train_cases=False
            )

            analysis = ANALYZER.analyze_run(run_dir)

            discovery = analysis["evidence_funnel"]["discovery_cases"]
            self.assertFalse(discovery["available"])
            self.assertIsNone(discovery["total"])
            self.assertEqual(discovery["datasets"], {})
            self.assertTrue(
                any("train_cases.json" in warning for warning in analysis["warnings"])
            )

    def test_node_only_glm_candidate_is_counterfactually_rejected_at_gate2(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            analysis = ANALYZER.analyze_run(self.make_glm_run(Path(temp_dir)))

            candidate = analysis["evaluated_candidates"][0]
            self.assertEqual(candidate["required_metrics"], ["llm_node_f1"])
            self.assertTrue(candidate["gate2"]["counterfactual"]["recorded_accepted"])
            self.assertFalse(candidate["gate2"]["counterfactual"]["accepted"])
            self.assertEqual(
                candidate["gate2"]["counterfactual"]["non_improving_required_metrics"],
                ["llm_node_f1"],
            )
            self.assertAlmostEqual(
                candidate["gate2"]["counterfactual"]["required_metric_results"]
                ["llm_node_f1"]["mean_delta"],
                -0.023,
            )

    def test_missing_dataset_measurement_is_not_treated_as_zero(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run(Path(temp_dir))
            registry_path = run_dir / "candidate_registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            applied_entry = next(
                entry
                for entry in registry["entries"]
                if entry["candidate_id"] == "cand_applied"
            )
            del applied_entry["validation_diagnostics"]["gate2_decision"][
                "per_dataset_metric_results"
            ]["pure"]
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            analysis = ANALYZER.analyze_run(run_dir)

            weighted = analysis["applied_candidates"][0]["gate2"]["metrics"][
                "llm_node_f1"
            ]["training_pool_weighted"]
            self.assertFalse(weighted["available"])
            self.assertIsNone(weighted["mean_delta"])
            self.assertEqual(weighted["missing_datasets"], ["pure"])

    def test_report_marks_weighted_metrics_as_diagnostic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            analysis = ANALYZER.analyze_run(self.make_run(Path(temp_dir)))

            report = ANALYZER.render_markdown([analysis])

            self.assertIn("diagnostic_only: true", report)
            self.assertIn("## Evidence Funnel", report)
            self.assertIn("## Required-metric Counterfactual", report)
            self.assertIn("fsd/fsd-0002", report)
            self.assertIn("+0.005451", report)
            self.assertIn("-0.011881", report)
            self.assertIn("+0.033900", report)

    def test_refuses_to_write_report_inside_input_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run(Path(temp_dir))

            with self.assertRaisesRegex(ValueError, "inside an input run"):
                ANALYZER.write_output("report", run_dir / "analysis.md", [run_dir])


if __name__ == "__main__":
    unittest.main()
