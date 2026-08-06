"""Canonical Prompt hashing shared by offline experiment tooling."""

from __future__ import annotations

import hashlib
from pathlib import Path


PROMPT_HASH_NORMALIZATION_VERSION = "utf8-sig+lf+strip-v1"


def canonical_prompt_text(text: str) -> str:
    """Normalize text exactly enough for cross-platform Prompt identity checks."""

    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def prompt_sha256(text: str) -> str:
    """Return the SHA-256 digest of canonical Prompt text."""

    canonical = canonical_prompt_text(text)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def prompt_file_sha256(path: Path) -> str:
    """Return the canonical digest of a UTF-8 Prompt file.

    ``utf-8-sig`` treats an optional BOM as an encoding marker, matching the
    way Prompt files are consumed rather than treating the BOM as content.
    """

    text = path.read_text(encoding="utf-8-sig")
    return prompt_sha256(text)
