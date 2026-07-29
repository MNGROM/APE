"""Run-local registry for Prompt candidates and exact group attempts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from utils.io import read_text, write_text


REGISTRY_VERSION = "candidate-registry-v1"


def prompt_fingerprint(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def load_candidate_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": REGISTRY_VERSION, "entries": [], "group_attempts": []}
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        raise ValueError(f"Candidate registry must be an object: {path}")
    if str(payload.get("version") or "") not in {"", REGISTRY_VERSION}:
        raise ValueError(
            f"Unsupported candidate registry version: {payload.get('version')!r}"
        )
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Candidate registry entries must be a list")
    group_attempts = payload.get("group_attempts", [])
    if not isinstance(group_attempts, list):
        raise ValueError("Candidate registry group_attempts must be a list")
    return {
        "version": REGISTRY_VERSION,
        "entries": [item for item in entries if isinstance(item, dict)],
        "group_attempts": [
            item for item in group_attempts if isinstance(item, dict)
        ],
    }


def save_candidate_registry(path: Path, registry: dict[str, Any]) -> None:
    entries = [
        item for item in registry.get("entries", []) if isinstance(item, dict)
    ]
    normalized = {
        "version": REGISTRY_VERSION,
        "entries": sorted(
            entries,
            key=lambda item: (
                str(item.get("base_prompt_hash") or ""),
                str(item.get("candidate_id") or ""),
            ),
        ),
        "group_attempts": sorted(
            (
                item
                for item in registry.get("group_attempts", [])
                if isinstance(item, dict)
            ),
            key=lambda item: (
                str(item.get("base_prompt_hash") or ""),
                str(item.get("group_signature") or ""),
                int(item.get("iteration") or 0),
                int(item.get("attempt") or 0),
            ),
        ),
    }
    write_text(path, json.dumps(normalized, ensure_ascii=False, indent=2))


def _normalized_finding_keys(finding_keys: list[Any]) -> list[str]:
    return sorted(
        {
            str(finding_key).strip()
            for finding_key in finding_keys
            if str(finding_key).strip()
        }
    )


def group_attempt_signature(
    *, base_prompt_hash: str, finding_keys: list[Any]
) -> str:
    normalized_keys = _normalized_finding_keys(finding_keys)
    if not base_prompt_hash or not normalized_keys:
        return ""
    payload = "\n".join([base_prompt_hash, *normalized_keys])
    return "group_attempt_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def group_attempt_history(
    registry: dict[str, Any], *, base_prompt_hash: str, finding_keys: list[Any]
) -> list[dict[str, Any]]:
    signature = group_attempt_signature(
        base_prompt_hash=base_prompt_hash, finding_keys=finding_keys
    )
    if not signature:
        return []
    return sorted(
        [
            item
            for item in registry.get("group_attempts", [])
            if isinstance(item, dict)
            and str(item.get("base_prompt_hash") or "") == base_prompt_hash
            and str(item.get("group_signature") or "") == signature
        ],
        key=lambda item: (
            int(item.get("iteration") or 0),
            int(item.get("attempt") or 0),
        ),
    )


def record_group_attempt(
    registry: dict[str, Any],
    *,
    iteration: int,
    attempt: int,
    base_prompt_hash: str,
    group_id: str,
    finding_keys: list[Any],
    outcome: str,
    rejection_reasons: list[Any],
    candidate_id: str = "",
) -> dict[str, Any]:
    normalized_keys = _normalized_finding_keys(finding_keys)
    signature = group_attempt_signature(
        base_prompt_hash=base_prompt_hash, finding_keys=normalized_keys
    )
    normalized_outcome = str(outcome).strip()
    if not signature:
        raise ValueError("Group attempt requires a base Prompt hash and finding keys")
    if not normalized_outcome:
        raise ValueError("Group attempt requires an outcome")
    attempt_id = "attempt_" + hashlib.sha256(
        f"{iteration}\n{attempt}\n{signature}".encode("utf-8")
    ).hexdigest()[:20]
    entries = [
        item
        for item in registry.setdefault("group_attempts", [])
        if isinstance(item, dict) and str(item.get("attempt_id") or "") != attempt_id
    ]
    entry = {
        "attempt_id": attempt_id,
        "iteration": int(iteration),
        "attempt": int(attempt),
        "base_prompt_hash": base_prompt_hash,
        "group_signature": signature,
        "group_id": str(group_id),
        "finding_keys": normalized_keys,
        "outcome": normalized_outcome,
        "rejection_reasons": [
            str(reason) for reason in rejection_reasons if str(reason)
        ],
        "candidate_id": str(candidate_id),
    }
    entries.append(entry)
    registry["group_attempts"] = entries
    return entry


def evaluated_candidate_ids(
    registry: dict[str, Any], *, base_prompt_hash: str
) -> set[str]:
    return {
        str(item.get("candidate_id") or "")
        for item in registry.get("entries", [])
        if isinstance(item, dict)
        and str(item.get("base_prompt_hash") or "") == base_prompt_hash
        and str(item.get("status") or "") == "evaluated"
        and str(item.get("candidate_id") or "")
    }


def record_evaluated_candidate(
    registry: dict[str, Any],
    *,
    iteration: int,
    base_prompt_hash: str,
    candidate_prompt: str,
    rule_text: str,
    candidate_metadata: dict[str, Any],
    validation_diagnostics: dict[str, Any],
    artifact_paths: dict[str, str],
) -> dict[str, Any]:
    candidate_id = str(candidate_metadata.get("candidate_id") or "")
    if not candidate_id:
        raise ValueError("Isolated candidate must have a Python-owned candidate_id")
    existing = [
        item
        for item in registry.setdefault("entries", [])
        if isinstance(item, dict)
        and str(item.get("base_prompt_hash") or "") == base_prompt_hash
        and str(item.get("candidate_id") or "") == candidate_id
    ]
    if any(str(item.get("status") or "") == "evaluated" for item in existing):
        raise ValueError(
            f"Candidate {candidate_id} was already recorded for base Prompt {base_prompt_hash}"
        )
    if existing:
        registry["entries"] = [
            item for item in registry["entries"] if item not in existing
        ]
    threshold_decision = validation_diagnostics.get(
        "threshold_decision", validation_diagnostics
    )
    invalid_reasons = (
        list(threshold_decision.get("invalid_reasons", []))
        if isinstance(threshold_decision, dict)
        else []
    )
    entry = {
        "candidate_id": candidate_id,
        "base_prompt_hash": base_prompt_hash,
        "candidate_prompt_hash": hashlib.sha256(
            candidate_prompt.encode("utf-8")
        ).hexdigest(),
        "rule_fragment_hash": hashlib.sha256(rule_text.encode("utf-8")).hexdigest(),
        "iteration": int(iteration),
        "status": "measurement_invalid" if invalid_reasons else "evaluated",
        "invalid_reasons": invalid_reasons,
        "validation_diagnostics": dict(validation_diagnostics),
        "artifacts": dict(artifact_paths),
    }
    entry.update(
        {
            "group_id": str(candidate_metadata.get("group_id") or ""),
            "finding_ids": list(candidate_metadata.get("finding_ids", [])),
            "finding_keys": list(candidate_metadata.get("finding_keys", [])),
            "positive_trigger": str(candidate_metadata.get("positive_trigger") or ""),
            "negative_boundary": str(candidate_metadata.get("negative_boundary") or ""),
        }
    )
    registry["entries"].append(entry)
    return entry
