import unittest
from collections import Counter

from ape_datasets.lato import Case
from run import build_parser, split_training_batches, split_validation_gate_cases


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


class TrainingBatchTest(unittest.TestCase):
    def test_parser_defaults_to_stratified_training_batches(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(args.training_batch_strategy, "stratified")
        self.assertTrue(args.validation_gate)
        self.assertEqual(args.validation_gate_strategy, "stratified")

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
