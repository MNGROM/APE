import types
import unittest

from analysis.behavior_contract import (
    compile_behavior_contract,
    evaluate_behavior_contract,
)


def _metrics(*, fn_nodes=(), fp_nodes=(), tp_nodes=(), fn_relations=(), fp_relations=(), tp_relations=()):
    return types.SimpleNamespace(
        enabled=True,
        status="success",
        matching={
            "nodes": {
                "fn": list(fn_nodes),
                "fp": list(fp_nodes),
                "tp": [{"gt": value, "pred": value} for value in tp_nodes],
            },
            "relations": {
                "fn": list(fn_relations),
                "fp": list(fp_relations),
                "tp": [{"gt": value, "pred": value} for value in tp_relations],
            },
        },
    )


def _record(case_id, metrics, *, compiled=True):
    return types.SimpleNamespace(
        dataset="data",
        case_id=case_id,
        llm_element_metrics=metrics,
        failure_types=[],
        plantuml_compilation=types.SimpleNamespace(passed=compiled),
    )


def _contract(anchor_kind="missing_node"):
    return compile_behavior_contract(
        selected_group={
            "group_id": "group_1",
            "members": [
                {
                    "finding_id": 1,
                    "finding_key": "finding_1",
                    "dataset": "data",
                    "case_id": "c1",
                    "anchor_kind": anchor_kind,
                    "error_anchor": "Approve request",
                    "requirement": "Approve request.",
                    "ground_truth": "@startuml\n:Approve request;\n@enduml",
                }
            ],
        },
        localization={"shared_repair": {"input_trigger": "explicit action"}},
    )


class BehaviorContractTest(unittest.TestCase):
    def test_repair_without_new_errors_is_proven(self):
        contract = _contract()
        baseline = _record("c1", _metrics(fn_nodes=["Approve request"]))
        candidate = _record("c1", _metrics(tp_nodes=["Approve request"]))

        decision = evaluate_behavior_contract(
            contract=contract, repeat_pairs=[(1, [baseline], [candidate])]
        )

        self.assertEqual(decision["status"], "proven")
        self.assertTrue(decision["proven"])
        self.assertEqual(decision["obligation_results"][0]["repeat_statuses"], ["repaired"])

    def test_unrelated_new_error_is_boundary_violation(self):
        contract = _contract()
        baseline = _record("c1", _metrics(fn_nodes=["Approve request"]))
        candidate = _record(
            "c1",
            _metrics(tp_nodes=["Approve request"], fp_nodes=["Invented action"]),
        )

        decision = evaluate_behavior_contract(
            contract=contract, repeat_pairs=[(1, [baseline], [candidate])]
        )

        self.assertEqual(decision["status"], "violated")
        self.assertEqual(
            decision["obligation_results"][0]["repeat_statuses"], ["boundary_violation"]
        )

    def test_missing_semantic_measurement_is_inconclusive(self):
        contract = _contract()
        baseline = _record("c1", types.SimpleNamespace(enabled=False, status="disabled"))
        candidate = _record("c1", types.SimpleNamespace(enabled=False, status="disabled"))

        decision = evaluate_behavior_contract(
            contract=contract, repeat_pairs=[(1, [baseline], [candidate])]
        )

        self.assertEqual(decision["status"], "inconclusive")
        self.assertFalse(decision["proven"])

    def test_compile_transition_for_compile_error(self):
        contract = _contract("compile_error")
        self.assertEqual(
            contract["obligations"][0]["expected_transition"], "compile_fail_to_pass"
        )


if __name__ == "__main__":
    unittest.main()
