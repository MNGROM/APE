import unittest
from collections import Counter

from ape_datasets.lato import Case
from run import (
    build_parser,
    resolve_pipeline_defaults,
    split_training_batches,
    split_gate_cases,
    split_gate1_cases,
    validate_glm_args,
)


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
    args.selector_thinking = "disabled"
    args.localization_thinking = "disabled"
    args.editor_thinking = "disabled"
    args.judge_thinking = "disabled"
    args.element_extraction_thinking = "disabled"
    resolve_pipeline_defaults(args)


class TrainingBatchTest(unittest.TestCase):
    def test_parser_defaults_to_stratified_training_batches(self) -> None:
        args = build_parser().parse_args([])

        self.assertEqual(args.training_batch_strategy, "stratified")
        self.assertEqual(args.epoch_batch_concurrency, 1)
        self.assertEqual(args.heldout_test_concurrency, 1)
        self.assertEqual(args.heldout_repeats, 1)
        self.assertEqual(args.gate_concurrency, 1)
        self.assertEqual(args.validation_repeats, 3)
        self.assertEqual(args.max_candidate_attempts_per_epoch, 3)
        self.assertFalse(args.stop_after_first_apply)
        self.assertFalse(hasattr(args, "acceptance_min_wins"))
        self.assertTrue(args.gate1)
        self.assertEqual(args.gate1_strategy, "stratified")
        self.assertTrue(args.gate2)
        self.assertEqual(args.gate2_size, 30)
        self.assertEqual(args.gate2_strategy, "stratified")
        self.assertEqual(args.gate2_seed, 20260630)
        self.assertTrue(args.llm_element_metrics)
        self.assertFalse(args.embedding_element_metrics)
        self.assertEqual(args.temperature, 0.0)
        self.assertEqual(args.analysis_temperature, 0.0)
        self.assertEqual(args.selector_temperature, 0.0)
        self.assertEqual(args.localization_temperature, 0.0)
        self.assertEqual(args.editor_temperature, 0.0)
        self.assertEqual(args.llm_judge_temperature, 0.0)
        self.assertEqual(args.element_extraction_temperature, 0.0)

    def test_nonzero_model_temperatures_are_rejected(self) -> None:
        temperature_options = (
            "--temperature",
            "--analysis-temperature",
            "--selector-temperature",
            "--localization-temperature",
            "--editor-temperature",
            "--llm-judge-temperature",
            "--element-extraction-temperature",
        )
        for option in temperature_options:
            with self.subTest(option=option):
                args = build_parser().parse_args([option, "0.2"])
                resolve_thinking_defaults(args)
                args.api_key = "dummy"

                with self.assertRaisesRegex(
                    ValueError, "All model temperatures must be 0"
                ):
                    validate_glm_args(args)

    def test_parser_accepts_epoch_batch_concurrency(self) -> None:
        args = build_parser().parse_args(["--epoch-batch-concurrency", "3"])

        self.assertEqual(args.epoch_batch_concurrency, 3)

    def test_parser_accepts_stop_after_first_apply(self) -> None:
        args = build_parser().parse_args(["--stop-after-first-apply"])

        self.assertTrue(args.stop_after_first_apply)

    def test_parser_accepts_heldout_test_concurrency(self) -> None:
        args = build_parser().parse_args(["--heldout-test-concurrency", "2"])

        self.assertEqual(args.heldout_test_concurrency, 2)

    def test_parser_accepts_heldout_repeats(self) -> None:
        args = build_parser().parse_args(["--heldout-repeats", "3"])

        self.assertEqual(args.heldout_repeats, 3)

    def test_heldout_repeats_must_be_positive(self) -> None:
        args = build_parser().parse_args(["--heldout-repeats", "0"])
        resolve_thinking_defaults(args)
        args.api_key = "dummy"

        with self.assertRaisesRegex(ValueError, "--heldout-repeats must be positive"):
            validate_glm_args(args)

    def test_parser_accepts_candidate_attempt_limit(self) -> None:
        args = build_parser().parse_args(["--max-candidate-attempts-per-epoch", "5"])

        self.assertEqual(args.max_candidate_attempts_per_epoch, 5)

    def test_parser_accepts_embedding_element_metrics(self) -> None:
        args = build_parser().parse_args(["--embedding-element-metrics"])

        self.assertTrue(args.embedding_element_metrics)

    def test_evolution_requires_gate1(self) -> None:
        args = build_parser().parse_args(
            [
                "--test-dataset",
                "us",
                "--no-validation-gate",
                "--candidate-application-mode",
                "cumulative",
            ]
        )
        resolve_thinking_defaults(args)
        args.api_key = "dummy"
        with self.assertRaisesRegex(ValueError, "requires an enabled"):
            validate_glm_args(args)

    def test_gate2_rejects_diagnostic_apply_bypass(self) -> None:
        args = build_parser().parse_args(
            ["--candidate-application-mode", "diagnostic-apply"]
        )
        resolve_thinking_defaults(args)
        args.api_key = "dummy"
        with self.assertRaisesRegex(ValueError, "cannot bypass"):
            validate_glm_args(args)

        args = build_parser().parse_args(
            ["--candidate-application-mode", "diagnostic-apply", "--no-gate2"]
        )
        resolve_thinking_defaults(args)
        args.api_key = "dummy"
        validate_glm_args(args)

    def test_isolated_mode_rejects_heldout_evaluation_during_search(self) -> None:
        args = build_parser().parse_args(
            [
                "--test-dataset",
                "us",
                "--eval-initial-test",
                "--candidate-application-mode",
                "isolated",
            ]
        )
        resolve_thinking_defaults(args)
        args.api_key = "dummy"

        with self.assertRaisesRegex(ValueError, "does not evaluate heldout"):
            validate_glm_args(args)

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

    def test_gate1_is_fixed_and_removed_from_training_cases(self) -> None:
        cases = make_cases("a", 10) + make_cases("b", 10)
        args = build_parser().parse_args([
            "--validation-gate-size",
            "6",
            "--validation-gate-seed",
            "123",
        ])

        optimize_cases, validation_cases = split_gate1_cases(cases, args)
        optimize_cases_again, validation_cases_again = split_gate1_cases(cases, args)

        validation_ids = {(case.dataset, case.case_id) for case in validation_cases}
        optimize_ids = {(case.dataset, case.case_id) for case in optimize_cases}
        self.assertEqual(len(validation_cases), 6)
        self.assertEqual(len(optimize_cases), 14)
        self.assertFalse(validation_ids & optimize_ids)
        self.assertEqual([case.case_id for case in validation_cases], [case.case_id for case in validation_cases_again])
        self.assertEqual([case.case_id for case in optimize_cases], [case.case_id for case in optimize_cases_again])
        self.assertEqual(Counter(case.dataset for case in validation_cases), Counter({"a": 3, "b": 3}))

    def test_gate1_size_is_capped_for_small_training_pools(self) -> None:
        cases = make_cases("a", 15) + make_cases("b", 15)
        args = build_parser().parse_args([
            "--validation-gate-size",
            "30",
        ])

        optimize_cases, validation_cases = split_gate1_cases(cases, args)

        self.assertEqual(len(validation_cases), 10)
        self.assertEqual(len(optimize_cases), 20)

    def test_validation_confirmation_and_training_splits_are_fixed_and_disjoint(self) -> None:
        cases = make_cases("a", 30) + make_cases("b", 30)
        args = build_parser().parse_args(
            [
                "--validation-gate-size",
                "10",
                "--validation-gate-seed",
                "123",
                "--gate2-size",
                "10",
                "--gate2-seed",
                "456",
            ]
        )

        first = split_gate_cases(cases, args)
        second = split_gate_cases(cases, args)
        train_cases, validation_cases, confirmation_cases = first
        id_sets = [
            {(case.dataset, case.case_id) for case in split}
            for split in first
        ]

        self.assertEqual([case.case_id for split in first for case in split], [case.case_id for split in second for case in split])
        self.assertEqual([len(train_cases), len(validation_cases), len(confirmation_cases)], [40, 10, 10])
        self.assertFalse(id_sets[0] & id_sets[1])
        self.assertFalse(id_sets[0] & id_sets[2])
        self.assertFalse(id_sets[1] & id_sets[2])
        self.assertEqual(Counter(case.dataset for case in confirmation_cases), Counter({"a": 5, "b": 5}))


if __name__ == "__main__":
    unittest.main()
