"""OpenAI-compatible chat-completions client."""

from __future__ import annotations

import dataclasses
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from config import DEFAULT_BASE_URL, DEFAULT_LLM_TIMEOUT, DEFAULT_MODEL, DEFAULT_THINKING_TYPE
from utils.rate_limit import ProviderHTTPError, call_with_provider_retries


def normalize_base_url(base_url: str) -> str:
    value = (base_url or DEFAULT_BASE_URL).strip().rstrip("/")
    suffix = "/chat/completions"
    if value.endswith(suffix):
        value = value[: -len(suffix)]
    return value + "/"


def post_chat_completion(*, endpoint: str, body: dict[str, Any], api_key: str, timeout: int) -> str:
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise ProviderHTTPError("LLM", exc.code, error_body, dict(exc.headers.items())) from exc

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected LLM response: {json.dumps(payload, ensure_ascii=False)[:1000]}") from exc
    return str(content or "").strip()


@dataclasses.dataclass
class LLMClient:
    model: str = DEFAULT_MODEL
    api_key: str = ""
    base_url: str = DEFAULT_BASE_URL
    temperature: float = 0.2
    top_p: float | None = None
    max_tokens: int = 12000
    thinking: str = DEFAULT_THINKING_TYPE
    do_sample: bool | None = None
    timeout: int = DEFAULT_LLM_TIMEOUT
    max_retries: int = 20
    retry_initial_wait: int = 30
    retry_max_wait: int = 600

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        thinking: str | None = None,
        state_dir: Path | None = None,
        retry_phase: str = "llm_request",
        retry_context: dict[str, Any] | None = None,
    ) -> str:
        if not self.api_key:
            raise RuntimeError("ZHIPU_LLM_API_KEY is required unless --mock-with-gold is used.")

        endpoint = normalize_base_url(self.base_url) + "chat/completions"
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
            "stream": False,
        }
        if self.top_p is not None:
            body["top_p"] = self.top_p
        if self.do_sample is not None:
            body["do_sample"] = self.do_sample
        thinking_type = self.thinking if thinking is None else thinking
        if thinking_type:
            body["thinking"] = {"type": thinking_type}
        return call_with_provider_retries(
            lambda: post_chat_completion(endpoint=endpoint, body=body, api_key=self.api_key, timeout=self.timeout),
            phase=retry_phase,
            state_dir=state_dir,
            context=retry_context,
            max_retries=self.max_retries,
            initial_wait=self.retry_initial_wait,
            max_wait=self.retry_max_wait,
        )
