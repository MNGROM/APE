import argparse
import unittest

from ape_datasets.lato import Case
from run import make_epoch_batches


def case(dataset: str, idx: int) -> Case:
    return Case(dataset=dataset, case_id=f"{dataset}-{idx:04d}", content="input", gold_plantuml="start\nstop")


class EpochBatchTest(unittest.TestCase):
    def test_stratified_epoch_batches_cover_all_cases_once(self) -> None:
        cases = [case("a", idx) for idx in range(4)] + [case("b", idx) for idx in range(3)]
        args = argparse.Namespace(sample_strategy="stratified", sample_seed=13, analysis_batch_size=3)

        batches = make_epoch_batches(cases, args=args, iteration=1)
        flattened = [item for batch in batches for item in batch]

        self.assertEqual([len(batch) for batch in batches], [3, 3, 1])
        self.assertCountEqual([item.case_id for item in flattened], [item.case_id for item in cases])
        self.assertEqual(len({item.case_id for item in flattened}), len(cases))


if __name__ == "__main__":
    unittest.main()
