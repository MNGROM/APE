import unittest
from collections import Counter

from ape_datasets.lato import Case
from run import build_parser, split_training_batches


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


if __name__ == "__main__":
    unittest.main()
