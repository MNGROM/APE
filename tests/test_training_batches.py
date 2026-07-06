import unittest
from collections import Counter

from ape_datasets.lato import Case
from run import build_parser, split_training_batches, split_validation_gate_cases, validate_glm_args


def make_cases(dataset: str, count: int) -> list[Case]:
    return [
        Case(
            dataset=dataset,
            case_id=f"{dataset}-{idx:04d}",
            content=f"{dataset} requirement {idx}",
            gold_plantuml="start\nstop",
        )
        for idx in range(1, count + 1)
    ]


def resolve_thinking_defaults(args) -> None:
    args.generation_thinking = "disabled"
    args.analysis_thinking = "disabled"
    args.localization_thinking = "disabled"
    args.editor_thinking = "disabled"
    args.epoch_planner_thinking = "disabled"
    args.judge_thinking = "disabled"
    args.element_extraction_thinking = "disabled"


class TrainingBatchTest(unittest.TestCase):
    def test_parser_defaults_to_stratified_training_batches(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(args.training_batch_strategy, "stratified")
        self.assertEqual(args.epoch_batch_concurrency, 1)
        self.assertEqual(args.heldout_test_concurrency, 1)
        self.assertTrue(args.validation_gate)
        self.assertEqual(args.validation_gate_strategy, "stratified")
        self.assertTrue(args.llm_element_metrics)
        self.assertFalse(args.embedding_element_metrics)

    def test_parser_accepts_epoch_batch_concurrency(self) -> None:
        args = build_parser().parse_args(["--epoch-batch-concurrency", "3"])

        self.assertEqual(args.epoch_batch_concurrency, 3)

    def test_parser_accepts_heldout_test_concurrency(self) -> None:
        args = build_parser().parse_args(["--heldout-test-concurrency", "2"])

        self.assertEqual(args.heldout_test_concurrency, 2)

    def test_parser_accepts_embedding_element_metrics(self) -> None:
        args = build_parser().parse_args(["--embedding-element-metrics"])

        self.assertTrue(args.embedding_element_metrics)

    def test_training_requires_llm_element_metrics(self) -> None:
        args = build_parser().parse_args(["--no-llm-element-metrics"])
        resolve_thinking_defaults(args)
        args.api_key = "dummy"
        args.llm_judge_api_key = "dummy"

        with self.assertRaisesRegex(ValueError, "--no-llm-element-metrics"):
            validate_glm_args(args)

        args = build_parser().parse_args(["--no-llm-element-metrics", "--no-evolve"])
        resolve_thinking_defaults(args)
        args.api_key = "dummy"
        args.llm_judge_api_key = "dummy"
        validate_glm_args(args)

    def test_chunked_training_batches_preserve_old_contiguous_split(self) -> None:
        cases = make_cases("a", 5) + make_cases("b", 5)

        batches = split_training_batches(cases, 4, strategy="chunked")

        self.assertEqual([[case.case_id for case in batch] for batch in batches], [
            ["a-0001", "a-0002", "a-0003", "a-0004"],
            ["a-0005", "b-0001", "b-0002", "b-0003"],
            ["b-0004", "b-0005"],
        ])

    def test_stratified_training_batches_mix_each_dataset_when_possible(self) -> None:
        cases = make_cases("a", 6) + make_cases("b", 6) + make_cases("c", 6)

        batches = split_training_batches(cases, 5, strategy="stratified")

        self.assertEqual(len(batches), 4)
        self.assertEqual(Counter(case.case_id for batch in batches for case in batch), Counter(case.case_id for case in cases))
        for batch in batches:
            self.assertEqual({case.dataset for case in batch}, {"a", "b", "c"})
        for dataset in {"a", "b", "c"}:
            counts = [sum(1 for case in batch if case.dataset == dataset) for batch in batches]
            self.assertLessEqual(max(counts) - min(counts), 1)

    def test_validation_gate_is_fixed_and_removed_from_training_cases(self) -> None:
        cases = make_cases("a", 10) + make_cases("b", 10)
        args = build_parser().parse_args([
            "--validation-gate-size",
            "6",
            "--validation-gate-seed",
            "123",
        ])

        optimize_cases, validation_cases = split_validation_gate_cases(cases, args)
        optimize_cases_again, validation_cases_again = split_validation_gate_cases(cases, args)

        validation_ids = {(case.dataset, case.case_id) for case in validation_cases}
        optimize_ids = {(case.dataset, case.case_id) for case in optimize_cases}
        self.assertEqual(len(validation_cases), 6)
        self.assertEqual(len(optimize_cases), 14)
        self.assertFalse(validation_ids & optimize_ids)
        self.assertEqual([case.case_id for case in validation_cases], [case.case_id for case in validation_cases_again])
        self.assertEqual([case.case_id for case in optimize_cases], [case.case_id for case in optimize_cases_again])
        self.assertEqual(Counter(case.dataset for case in validation_cases), Counter({"a": 3, "b": 3}))

    def test_validation_gate_size_is_capped_for_small_training_pools(self) -> None:
        cases = make_cases("a", 15) + make_cases("b", 15)
        args = build_parser().parse_args([
            "--validation-gate-size",
            "30",
        ])

        optimize_cases, validation_cases = split_validation_gate_cases(cases, args)

        self.assertEqual(len(validation_cases), 10)
        self.assertEqual(len(optimize_cases), 20)


if __name__ == "__main__":
    unittest.main()
