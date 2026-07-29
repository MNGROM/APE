"""Shared configuration constants for APE prompt evolution."""

from __future__ import annotations

import argparse
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
DEFAULT_LLM_TIMEOUT = 300
DEFAULT_THINKING_TYPE = "disabled"

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
