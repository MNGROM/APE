"""Shared configuration constants for APE prompt evolution."""

from __future__ import annotations

import argparse
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is optional.
    load_dotenv = None


PROJECT_DIR = Path(__file__).resolve().parent
if load_dotenv is not None:
    load_dotenv(PROJECT_DIR / ".env", override=False)

DEFAULT_DATASETS_DIR = PROJECT_DIR / "prompt_datasets" / "lato"
DEFAULT_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "tst.md"
DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "failure_analysis_selector_v2.md"
DEFAULT_ERROR_SELECTOR_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "error_selector_v4.md"
DEFAULT_ERROR_LOCALIZATION_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "prompt_gap_localization_v2.md"
DEFAULT_PROMPT_EDITOR_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "prompt_editor_selector_v2.md"
DEFAULT_PROMPT_REWRITER_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "prompt_rewriter_selector_v1.md"
DEFAULT_RUNS_DIR = PROJECT_DIR / "prompt_runs"
DEFAULT_PLANTUML_JAR = PROJECT_DIR / "tools" / "plantuml" / "plantuml-1.2025.4.jar"
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
DEFAULT_MODEL = "glm-5.1"
DEFAULT_LLM_PROVIDER = "zhipu"
DEEPSEEK_DEFAULT_BASE_URL = "https://api.deepseek.com/"
DEEPSEEK_DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_LLM_TIMEOUT = 300
DEFAULT_THINKING_TYPE = "disabled"


@dataclass(frozen=True)
class LLMProviderSettings:
    name: str
    api_key: str
    api_key_environment: str
    base_url: str
    model: str
    generation_model: str | None
    agent_model: str | None
    judge_model: str | None
    judge_api_key: str
    judge_base_url: str
    thinking: str
    generation_thinking: str
    analysis_thinking: str
    selector_thinking: str
    localization_thinking: str
    editor_thinking: str
    judge_thinking: str
    element_extraction_thinking: str
    do_sample: bool | None


def _environment_value(
    environment: Mapping[str, str],
    name: str,
    default: str | None = None,
) -> str | None:
    value = str(environment.get(name, "") or "").strip()
    return value if value else default


def resolve_llm_provider(environment: Mapping[str, str] | None = None) -> str:
    """Resolve the active provider without silently choosing between two keys."""

    environment = os.environ if environment is None else environment
    requested = str(environment.get("APE_LLM_PROVIDER", "") or "").strip().lower()
    if requested:
        if requested not in {"zhipu", "deepseek"}:
            raise ValueError("APE_LLM_PROVIDER must be 'zhipu' or 'deepseek'")
        return requested

    has_zhipu_key = bool(_environment_value(environment, "ZHIPU_LLM_API_KEY"))
    has_deepseek_key = bool(_environment_value(environment, "DEEPSEEK_API_KEY"))
    if has_zhipu_key and has_deepseek_key:
        raise ValueError(
            "Both ZHIPU_LLM_API_KEY and DEEPSEEK_API_KEY are set; "
            "set APE_LLM_PROVIDER explicitly"
        )
    if has_deepseek_key:
        return "deepseek"
    return DEFAULT_LLM_PROVIDER


def get_llm_provider_settings(
    environment: Mapping[str, str] | None = None,
) -> LLMProviderSettings:
    """Return provider-specific CLI defaults resolved from environment variables."""

    environment = os.environ if environment is None else environment
    provider = resolve_llm_provider(environment)
    if provider == "deepseek":
        api_key = _environment_value(environment, "DEEPSEEK_API_KEY", "") or ""
        base_url = _environment_value(
            environment,
            "DEEPSEEK_BASE_URL",
            DEEPSEEK_DEFAULT_BASE_URL,
        ) or DEEPSEEK_DEFAULT_BASE_URL
        model = _environment_value(
            environment,
            "DEEPSEEK_MODEL",
            DEEPSEEK_DEFAULT_MODEL,
        ) or DEEPSEEK_DEFAULT_MODEL
        thinking = _environment_value(
            environment,
            "DEEPSEEK_THINKING_TYPE",
            DEFAULT_THINKING_TYPE,
        ) or DEFAULT_THINKING_TYPE
        return LLMProviderSettings(
            name=provider,
            api_key=api_key,
            api_key_environment="DEEPSEEK_API_KEY",
            base_url=base_url,
            model=model,
            generation_model=_environment_value(environment, "DEEPSEEK_GENERATION_MODEL"),
            agent_model=_environment_value(environment, "DEEPSEEK_AGENT_MODEL"),
            judge_model=_environment_value(environment, "DEEPSEEK_JUDGE_MODEL"),
            judge_api_key=_environment_value(
                environment,
                "DEEPSEEK_JUDGE_API_KEY",
                api_key,
            ) or api_key,
            judge_base_url=_environment_value(
                environment,
                "DEEPSEEK_JUDGE_BASE_URL",
                base_url,
            ) or base_url,
            thinking=thinking,
            generation_thinking=_environment_value(
                environment,
                "DEEPSEEK_GENERATION_THINKING_TYPE",
                "inherit",
            ) or "inherit",
            analysis_thinking=_environment_value(
                environment,
                "DEEPSEEK_ANALYSIS_THINKING_TYPE",
                "inherit",
            ) or "inherit",
            selector_thinking=_environment_value(
                environment,
                "DEEPSEEK_SELECTOR_THINKING_TYPE",
                "inherit",
            ) or "inherit",
            localization_thinking=_environment_value(
                environment,
                "DEEPSEEK_LOCALIZATION_THINKING_TYPE",
                "inherit",
            ) or "inherit",
            editor_thinking=_environment_value(
                environment,
                "DEEPSEEK_EDITOR_THINKING_TYPE",
                "inherit",
            ) or "inherit",
            judge_thinking=_environment_value(
                environment,
                "DEEPSEEK_JUDGE_THINKING_TYPE",
                "inherit",
            ) or "inherit",
            element_extraction_thinking=_environment_value(
                environment,
                "DEEPSEEK_ELEMENT_EXTRACTION_THINKING_TYPE",
                "inherit",
            ) or "inherit",
            do_sample=None,
        )

    api_key = _environment_value(environment, "ZHIPU_LLM_API_KEY", "") or ""
    base_url = _environment_value(
        environment,
        "ZHIPU_LLM_BASE_URL",
        DEFAULT_BASE_URL,
    ) or DEFAULT_BASE_URL
    model = _environment_value(
        environment,
        "ZHIPU_LLM_MODEL",
        DEFAULT_MODEL,
    ) or DEFAULT_MODEL
    thinking = _environment_value(
        environment,
        "ZHIPU_THINKING_TYPE",
        DEFAULT_THINKING_TYPE,
    ) or DEFAULT_THINKING_TYPE
    return LLMProviderSettings(
        name=provider,
        api_key=api_key,
        api_key_environment="ZHIPU_LLM_API_KEY",
        base_url=base_url,
        model=model,
        generation_model=_environment_value(environment, "ZHIPU_LLM_GENERATION_MODEL"),
        agent_model=_environment_value(environment, "ZHIPU_LLM_AGENT_MODEL"),
        judge_model=_environment_value(environment, "ZHIPU_LLM_JUDGE_MODEL"),
        judge_api_key=_environment_value(
            environment,
            "ZHIPU_LLM_JUDGE_API_KEY",
            api_key,
        ) or api_key,
        judge_base_url=_environment_value(
            environment,
            "ZHIPU_LLM_JUDGE_BASE_URL",
            base_url,
        ) or base_url,
        thinking=thinking,
        generation_thinking=_environment_value(
            environment,
            "ZHIPU_GENERATION_THINKING_TYPE",
            "inherit",
        ) or "inherit",
        analysis_thinking=_environment_value(
            environment,
            "ZHIPU_ANALYSIS_THINKING_TYPE",
            "inherit",
        ) or "inherit",
        selector_thinking=_environment_value(
            environment,
            "ZHIPU_SELECTOR_THINKING_TYPE",
            "inherit",
        ) or "inherit",
        localization_thinking=_environment_value(
            environment,
            "ZHIPU_LOCALIZATION_THINKING_TYPE",
            "inherit",
        ) or "inherit",
        editor_thinking=_environment_value(
            environment,
            "ZHIPU_EDITOR_THINKING_TYPE",
            "inherit",
        ) or "inherit",
        judge_thinking=_environment_value(
            environment,
            "ZHIPU_JUDGE_THINKING_TYPE",
            "inherit",
        ) or "inherit",
        element_extraction_thinking=_environment_value(
            environment,
            "ZHIPU_ELEMENT_EXTRACTION_THINKING_TYPE",
            "inherit",
        ) or "inherit",
        do_sample=False,
    )

REQUIRED_PROMPT_HEADINGS = (
    "## agent task",
    "## input",
    "## output",
    "## workflow",
    "## knowledge",
    "## rule",
)
SECTION_NAMES = tuple(heading.replace("## ", "") for heading in REQUIRED_PROMPT_HEADINGS)
SECTION_HEADING_BY_NAME = dict(zip(SECTION_NAMES, REQUIRED_PROMPT_HEADINGS))


def optional_float(value: str) -> float | None:
    if value.lower() in {"none", "omit", "default", ""}:
        return None
    return float(value)


def optional_bool(value: str) -> bool | None:
    lowered = value.lower()
    if lowered in {"none", "omit", "default", ""}:
        return None
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("expected true, false, or omit")
