"""Shared rate-limit retry helpers for provider API calls."""

from __future__ import annotations

import json
import random
import threading
import time
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable


RATE_LIMIT_STATUS_CODES = {429}
RATE_LIMIT_ERROR_CODES = {"1302"}
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_STATE_LOCK = threading.Lock()


class ProviderHTTPError(RuntimeError):
    """HTTP error raised by LLM provider calls."""

    def __init__(self, prefix: str, status_code: int, body: str, headers: dict[str, str] | None = None) -> None:
        self.prefix = prefix
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}
        super().__init__(f"{prefix} HTTP {status_code}: {body[:1000]}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def parse_error_code(body: str) -> str:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return ""
    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        return str(error.get("code") or "")
    return str(payload.get("code") or "") if isinstance(payload, dict) else ""


def is_rate_limit_error(error: BaseException) -> bool:
    if isinstance(error, ProviderHTTPError):
        if error.status_code in RATE_LIMIT_STATUS_CODES:
            return True
        return parse_error_code(error.body) in RATE_LIMIT_ERROR_CODES
    lowered = str(error).lower()
    return "http 429" in lowered or '"code":"1302"' in lowered or "rate limit" in lowered or "速率限制" in lowered


def is_retryable_provider_error(error: BaseException) -> bool:
    if isinstance(error, ProviderHTTPError):
        return error.status_code in RETRYABLE_STATUS_CODES or is_rate_limit_error(error)
    lowered = str(error).lower()
    return any(
        marker in lowered
        for marker in (
            "timed out",
            "incompleteread",
            "ssl:",
            "urlopen error",
            "connection reset",
            "remote end closed",
            "temporary failure",
            "http 429",
            "http 500",
            "http 502",
            "http 503",
            "http 504",
        )
    )


def retry_after_seconds(headers: dict[str, str], *, cap_seconds: int) -> int | None:
    value = ""
    for key, header_value in headers.items():
        if key.lower() == "retry-after":
            value = header_value.strip()
            break
    if not value:
        return None
    if value.isdigit():
        return max(0, min(int(value), cap_seconds))
    try:
        retry_time = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if retry_time.tzinfo is None:
        return None
    wait = int((retry_time - datetime.now(retry_time.tzinfo)).total_seconds())
    return max(0, min(wait, cap_seconds))


def sanitized_error(error: BaseException) -> dict[str, Any]:
    if isinstance(error, ProviderHTTPError):
        return {
            "type": type(error).__name__,
            "prefix": error.prefix,
            "status_code": error.status_code,
            "provider_error_code": parse_error_code(error.body),
            "body_excerpt": error.body[:1000],
        }
    return {"type": type(error).__name__, "message": str(error)[:1000]}


def save_retry_state(
    *,
    state_dir: Path | None,
    event: dict[str, Any],
) -> None:
    if state_dir is None:
        return
    with _STATE_LOCK:
        write_text(state_dir / "run_state.json", json.dumps(event, ensure_ascii=False, indent=2))
        append_jsonl(state_dir / "rate_limit_events.jsonl", event)


def call_with_provider_retries(
    operation: Callable[[], str],
    *,
    phase: str,
    state_dir: Path | None,
    context: dict[str, Any] | None = None,
    max_retries: int = 20,
    initial_wait: int = 30,
    max_wait: int = 600,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> str:
    """Call an LLM provider operation with retry/backoff for transient failures."""

    attempts = max(1, max_retries + 1)
    wait_base = max(0, initial_wait)
    wait_cap = max(wait_base, max_wait)
    context = context or {}

    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:
            retryable = is_retryable_provider_error(exc)
            if not retryable or attempt >= attempts:
                raise

            header_wait = retry_after_seconds(getattr(exc, "headers", {}) or {}, cap_seconds=wait_cap)
            backoff_wait = min(wait_cap, wait_base * (2 ** (attempt - 1))) if wait_base > 0 else 0
            jitter = random.uniform(0, min(5.0, max(0.0, float(backoff_wait) * 0.1)))
            wait_seconds = int(header_wait if header_wait is not None else backoff_wait + jitter)
            retry_at = datetime.now() + timedelta(seconds=wait_seconds)
            event = {
                "updated_at": datetime.now().isoformat(timespec="seconds"),
                "phase": phase,
                "attempt": attempt,
                "max_retries": max_retries,
                "retryable": retryable,
                "rate_limited": is_rate_limit_error(exc),
                "wait_seconds": wait_seconds,
                "retry_at": retry_at.isoformat(timespec="seconds"),
                "context": context,
                "error": sanitized_error(exc),
            }
            save_retry_state(state_dir=state_dir, event=event)
            label = "rate limit" if event["rate_limited"] else "transient provider error"
            print(
                f"[llm-retry] {label} during {phase}; attempt {attempt}/{max_retries}, "
                f"waiting {wait_seconds}s before retry",
                flush=True,
            )
            if wait_seconds > 0:
                sleep_fn(wait_seconds)

    raise RuntimeError("unreachable retry loop state")
