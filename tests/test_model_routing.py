import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ape_datasets.lato import Case
from llm import LLMClient
from llm_element_metrics import (
    _clean_optional_body_fields,
    evaluate_llm_elements,
    judge_chat,
)
from prediction import generated_from_args
from run import build_parser, make_llm_client, resolve_model_roles


class RecordingClient:
    def __init__(self, model: str, root: "RecordingClient | None" = None) -> None:
        self.model = model
        self.root = root or self
        self.routed_models: list[str] = []
        self.calls: list[str] = []

    def for_model(self, model: str) -> "RecordingClient":
        self.root.routed_models.append(model)
        return RecordingClient(model, self.root)

    def chat(self, messages, **kwargs):
        self.root.calls.append(self.model)
        return "@startuml\nstart\nstop\n@enduml"


class ModelRoutingTest(unittest.TestCase):
    def test_llm_client_defaults_to_zero_temperature(self):
        self.assertEqual(LLMClient().temperature, 0.0)

    def test_llm_client_rejects_nonzero_temperature(self):
        client = LLMClient(api_key="key", temperature=0.0)

        with self.assertRaisesRegex(ValueError, "LLM temperature must be 0"):
            client.chat([{"role": "user", "content": "test"}], temperature=0.2)

    def test_legacy_model_fallback_and_explicit_roles(self):
        args = build_parser().parse_args([
            "--model", "legacy-model",
            "--generation-model", "glm-4.5",
            "--agent-model", "glm-5.1",
            "--judge-model", "glm-5.1",
        ])
        resolve_model_roles(args)

        self.assertEqual(args.generation_model, "glm-4.5")
        self.assertEqual(args.agent_model, "glm-5.1")
        self.assertEqual(args.judge_model, "glm-5.1")
        self.assertEqual(args.llm_judge_model, "glm-5.1")
        self.assertEqual(make_llm_client(args).model, "glm-5.1")
        self.assertFalse(args.do_sample)
        self.assertFalse(make_llm_client(args).do_sample)

        fallback = build_parser().parse_args(["--model", "legacy-model"])
        resolve_model_roles(fallback)
        self.assertEqual(
            (fallback.generation_model, fallback.agent_model, fallback.judge_model),
            ("legacy-model", "legacy-model", "legacy-model"),
        )

    def test_sampling_requires_explicit_opt_in(self):
        parser = build_parser()

        self.assertFalse(parser.parse_args([]).do_sample)
        self.assertTrue(parser.parse_args(["--do-sample", "true"]).do_sample)
        self.assertIsNone(parser.parse_args(["--do-sample", "omit"]).do_sample)

    def test_prediction_routes_only_to_generation_model(self):
        args = SimpleNamespace(
            generation_model="glm-4.5",
            mock_with_gold=False,
            generation_thinking="disabled",
        )
        client = RecordingClient("glm-5.1")
        generated = generated_from_args(
            prompt="prompt",
            case=Case("fsd", "fsd-0001", "Requirement.", "start\nstop"),
            args=args,
            llm_client=client,
            state_dir=None,
            retry_phase="test",
        )

        self.assertIn("@startuml", generated)
        self.assertEqual(client.routed_models, ["glm-4.5"])
        self.assertEqual(client.calls, ["glm-4.5"])

    def test_for_model_preserves_client_transport_settings(self):
        client = LLMClient(
            model="glm-5.1", api_key="key", base_url="https://example.invalid/v4/",
            temperature=0.0, max_tokens=321, thinking="disabled", timeout=17,
        )
        routed = client.for_model("glm-4.5")

        self.assertEqual(routed.model, "glm-4.5")
        self.assertEqual(routed.api_key, client.api_key)
        self.assertEqual(routed.base_url, client.base_url)
        self.assertEqual(routed.max_tokens, client.max_tokens)
        self.assertIsNot(routed, client)

    def test_chat_sends_the_routed_model_in_request_body(self):
        client = LLMClient(
            model="glm-5.1", api_key="key", base_url="https://example.invalid/v4/",
            temperature=0.0, thinking="disabled", max_retries=0,
        ).for_model("glm-4.5")
        captured = {}

        def fake_post(*, endpoint, body, api_key, timeout):
            captured.update(body)
            return "ok"

        with patch("llm.post_chat_completion", side_effect=fake_post):
            result = client.chat([{"role": "user", "content": "test"}])

        self.assertEqual(result, "ok")
        self.assertEqual(captured["model"], "glm-4.5")
        self.assertIs(captured["do_sample"], False)

    def test_judge_request_disables_sampling(self):
        captured = {}

        def fake_post(*, endpoint, body, api_key, timeout):
            captured.update(body)
            return "ok"

        with patch("llm_element_metrics.post_chat_completion", side_effect=fake_post):
            result = judge_chat(
                messages=[{"role": "user", "content": "test"}],
                model="glm-5.1",
                api_key="key",
                base_url="https://example.invalid/v4/",
                temperature=0.0,
                max_tokens=128,
                timeout=10,
                thinking="disabled",
                do_sample=False,
                provider_max_retries=0,
            )

        self.assertEqual(result, "ok")
        self.assertIs(captured["do_sample"], False)

    def test_judge_rejects_nonzero_temperature(self):
        with self.assertRaisesRegex(ValueError, "LLM temperature must be 0"):
            judge_chat(
                messages=[{"role": "user", "content": "test"}],
                model="glm-5.1",
                api_key="key",
                base_url="https://example.invalid/v4/",
                temperature=0.2,
                max_tokens=128,
                timeout=10,
                thinking="disabled",
                provider_max_retries=0,
            )

    def test_judge_pipeline_threads_sampling_mode_to_every_call(self):
        responses = [
            '{"nodes": [], "relations": []}',
            '{"nodes": [], "relations": []}',
            '{"nodes": {"tp": [], "fp": [], "fn": []}, "relations": {"tp": [], "fp": [], "fn": []}}',
        ]
        with patch("llm_element_metrics.judge_chat", side_effect=responses) as mocked:
            result = evaluate_llm_elements(
                ground_truth="start\nstop",
                prediction="start\nstop",
                enabled=True,
                model="glm-5.1",
                api_key="key",
                base_url="https://example.invalid/v4/",
                do_sample=False,
                max_retries=1,
            )

        self.assertEqual(result.status, "success")
        self.assertEqual(mocked.call_count, 3)
        self.assertTrue(all(call.kwargs["do_sample"] is False for call in mocked.call_args_list))

    def test_compatibility_retry_never_removes_sampling_control(self):
        body = {"do_sample": False, "thinking": {"type": "disabled"}}

        self.assertIsNone(
            _clean_optional_body_fields(body, RuntimeError("do_sample is unsupported"))
        )


if __name__ == "__main__":
    unittest.main()
