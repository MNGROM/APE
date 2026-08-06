import os
import sys
import unittest
from unittest.mock import patch

from config import (
    DEEPSEEK_DEFAULT_BASE_URL,
    DEEPSEEK_DEFAULT_MODEL,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    get_llm_provider_settings,
    resolve_llm_provider,
)
from llm import LLMClient, is_deepseek_base_url, should_send_sampling_control
from llm_element_metrics import judge_chat


class ProviderConfigTest(unittest.TestCase):
    def test_zhipu_settings_keep_existing_defaults(self) -> None:
        settings = get_llm_provider_settings(
            {
                "ZHIPU_LLM_API_KEY": "zhipu-secret",
            }
        )

        self.assertEqual(settings.name, "zhipu")
        self.assertEqual(settings.api_key, "zhipu-secret")
        self.assertEqual(settings.base_url, DEFAULT_BASE_URL)
        self.assertEqual(settings.model, DEFAULT_MODEL)
        self.assertFalse(settings.do_sample)

    def test_deepseek_settings_infer_from_key_and_use_env_overrides(self) -> None:
        settings = get_llm_provider_settings(
            {
                "DEEPSEEK_API_KEY": "deepseek-secret",
                "DEEPSEEK_MODEL": "deepseek-test-model",
                "DEEPSEEK_BASE_URL": "https://proxy.example/v1/",
                "DEEPSEEK_JUDGE_MODEL": "deepseek-judge-model",
            }
        )

        self.assertEqual(resolve_llm_provider({"DEEPSEEK_API_KEY": "key"}), "deepseek")
        self.assertEqual(settings.name, "deepseek")
        self.assertEqual(settings.api_key, "deepseek-secret")
        self.assertEqual(settings.base_url, "https://proxy.example/v1/")
        self.assertEqual(settings.model, "deepseek-test-model")
        self.assertEqual(settings.judge_model, "deepseek-judge-model")
        self.assertIsNone(settings.do_sample)

    def test_deepseek_defaults_are_official_endpoint_and_model(self) -> None:
        settings = get_llm_provider_settings({"DEEPSEEK_API_KEY": "key"})

        self.assertEqual(settings.base_url, DEEPSEEK_DEFAULT_BASE_URL)
        self.assertEqual(settings.model, DEEPSEEK_DEFAULT_MODEL)
        self.assertEqual(settings.api_key_environment, "DEEPSEEK_API_KEY")

    def test_two_keys_require_explicit_provider(self) -> None:
        with self.assertRaisesRegex(ValueError, "set APE_LLM_PROVIDER explicitly"):
            resolve_llm_provider(
                {
                    "ZHIPU_LLM_API_KEY": "zhipu",
                    "DEEPSEEK_API_KEY": "deepseek",
                }
            )

        self.assertEqual(
            resolve_llm_provider(
                {
                    "APE_LLM_PROVIDER": "deepseek",
                    "ZHIPU_LLM_API_KEY": "zhipu",
                    "DEEPSEEK_API_KEY": "deepseek",
                }
            ),
            "deepseek",
        )

    def test_entrypoint_parsers_read_deepseek_environment(self) -> None:
        import compare_lato_eval
        import eval_seed_prompt_all
        import run

        environment = {
            "APE_LLM_PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "deepseek-secret",
            "DEEPSEEK_MODEL": "deepseek-parser-model",
            "DEEPSEEK_BASE_URL": "https://api.deepseek.com/",
        }
        with patch.dict(os.environ, environment, clear=True):
            run_args = run.build_parser().parse_args([])
            seed_args = eval_seed_prompt_all.build_parser().parse_args(["--mock-with-gold"])
            compare_args = compare_lato_eval.build_parser().parse_args([])

        for args in (run_args, seed_args, compare_args):
            self.assertEqual(args.llm_provider, "deepseek")
            self.assertEqual(args.api_key, "deepseek-secret")
            self.assertEqual(args.model, "deepseek-parser-model")
            self.assertEqual(args.base_url, "https://api.deepseek.com/")
            self.assertIsNone(args.do_sample)

    def test_deepseek_never_sends_do_sample_even_if_internal_default_is_false(self) -> None:
        captured: dict[str, object] = {}
        captured_endpoint: list[str] = []

        def fake_post(*, endpoint, body, api_key, timeout):
            captured_endpoint.append(endpoint)
            captured.update(body)
            return "ok"

        with patch("llm.post_chat_completion", side_effect=fake_post):
            result = LLMClient(
                model="deepseek-v4-flash",
                api_key="key",
                base_url="https://api.deepseek.com/v1/",
                temperature=0.0,
                thinking="disabled",
                do_sample=False,
                max_retries=0,
            ).chat([{"role": "user", "content": "test"}])

        self.assertEqual(result, "ok")
        self.assertEqual(captured_endpoint, ["https://api.deepseek.com/v1/chat/completions"])
        self.assertEqual(captured["temperature"], 0.0)
        self.assertEqual(captured["thinking"], {"type": "disabled"})
        self.assertNotIn("do_sample", captured)

    def test_deepseek_element_judge_omits_do_sample(self) -> None:
        captured: dict[str, object] = {}

        def fake_post(*, endpoint, body, api_key, timeout):
            captured.update(body)
            return "ok"

        with patch("llm_element_metrics.post_chat_completion", side_effect=fake_post):
            result = judge_chat(
                messages=[{"role": "user", "content": "test"}],
                model="deepseek-v4-flash",
                api_key="key",
                base_url="https://api.deepseek.com/",
                temperature=0.0,
                max_tokens=128,
                timeout=10,
                thinking="disabled",
                do_sample=False,
                provider_max_retries=0,
            )

        self.assertEqual(result, "ok")
        self.assertNotIn("do_sample", captured)

    def test_deepseek_url_detection_does_not_hide_sampling_for_other_hosts(self) -> None:
        self.assertTrue(is_deepseek_base_url("https://api.deepseek.com"))
        self.assertTrue(is_deepseek_base_url("api.deepseek.com/v1"))
        self.assertFalse(is_deepseek_base_url("https://example.com/deepseek"))
        self.assertFalse(should_send_sampling_control("https://api.deepseek.com", False))
        self.assertTrue(should_send_sampling_control("https://example.com/v1", False))

    def test_compare_entrypoint_rejects_nonzero_temperature(self) -> None:
        import compare_lato_eval

        with patch.object(
            sys,
            "argv",
            ["compare_lato_eval.py", "--mock-with-gold", "--temperature", "0.1"],
        ):
            with self.assertRaisesRegex(RuntimeError, "All model temperatures must be 0"):
                compare_lato_eval.main()


if __name__ == "__main__":
    unittest.main()
