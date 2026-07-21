"""Run-local evidence memory for open mechanism hypotheses."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from utils.io import read_text, write_text


MEMORY_VERSION = "memory-v1"


def prompt_fingerprint(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def evidence_fingerprint(
    *,
    prompt_hash: str,
    attribution: dict[str, Any],
    evidence: dict[str, Any],
) -> str:
    canonical = {
        "prompt_hash": prompt_hash,
        "dataset": str(evidence.get("dataset") or ""),
        "case_id": str(evidence.get("case_id") or ""),
        "anchor_kind": str(attribution.get("anchor_kind") or ""),
        "anchor_locator": str(attribution.get("error_anchor") or ""),
        "requirement_quote": str(attribution.get("requirement_quote") or ""),
    }
    serialized = json.dumps(canonical, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def load_memory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": MEMORY_VERSION, "entries": []}
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        raise ValueError(f"Mechanism memory must be an object: {path}")
    version = str(payload.get("version") or "")
    if version not in {MEMORY_VERSION, ""}:
        raise ValueError(f"Unsupported mechanism memory version: {version!r}")
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Mechanism memory entries must be a list")
    return {"version": MEMORY_VERSION, "entries": [item for item in entries if isinstance(item, dict)]}


def save_memory(path: Path, memory: dict[str, Any]) -> None:
    normalized = {
        "version": MEMORY_VERSION,
        "entries": sorted(
            [item for item in memory.get("entries", []) if isinstance(item, dict)],
            key=lambda item: (
                str(item.get("prompt_hash") or ""),
                str(item.get("evidence_fingerprint") or ""),
            ),
        ),
    }
    write_text(path, json.dumps(normalized, ensure_ascii=False, indent=2))


def active_memory_entries(
    memory: dict[str, Any], *, prompt_hash: str, taxonomy_version: str
) -> list[dict[str, Any]]:
    return [
        item
        for item in memory.get("entries", [])
        if isinstance(item, dict)
        and str(item.get("prompt_hash") or "") == prompt_hash
        and str(item.get("taxonomy_version") or "") == taxonomy_version
        and str(item.get("status") or "") not in {"historical", "rejected"}
    ]


def record_observations(
    memory: dict[str, Any],
    observations: Iterable[dict[str, Any]],
    *,
    prompt_hash: str,
    taxonomy_version: str,
    iteration: int,
) -> dict[str, Any]:
    """Upsert exact attribution/evidence pairs without trusting model IDs."""

    entries = memory.setdefault("entries", [])
    by_fingerprint = {
        str(item.get("evidence_fingerprint") or ""): item
        for item in entries
        if isinstance(item, dict) and str(item.get("evidence_fingerprint") or "")
    }
    for item in entries:
        if (
            isinstance(item, dict)
            and str(item.get("prompt_hash") or "") != prompt_hash
            and str(item.get("status") or "") != "historical"
        ):
            item["status"] = "historical"

    for observation in observations:
        if not isinstance(observation, dict):
            continue
        attributions = [
            item
            for item in observation.get("attributions", [])
            if isinstance(item, dict)
        ]
        evidence_by_id = {
            str(item.get("evidence_id") or ""): item
            for item in (
                observation.get("evidence_catalog")
                or observation.get("supporting_evidence", [])
            )
            if isinstance(item, dict) and str(item.get("evidence_id") or "")
        }
        for attribution in attributions:
            evidence_id = str(attribution.get("evidence_id") or "")
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                continue
            fingerprint = evidence_fingerprint(
                prompt_hash=prompt_hash,
                attribution=attribution,
                evidence=evidence,
            )
            candidate_eligible = bool(
                observation.get("candidate_eligible")
                and attribution.get("role") == "primary"
                and str(attribution.get("matching_quality") or "") in {"bijective", "not_available", ""}
            )
            existing = by_fingerprint.get(fingerprint)
            if existing is None:
                existing = {
                    "evidence_fingerprint": fingerprint,
                    "hypothesis_id": str(observation.get("hypothesis_id") or ""),
                    "mechanism_id": str(observation.get("mechanism_id") or ""),
                    "parent_key": list(observation.get("parent_key") or []),
                    "child_key": list(observation.get("child_key") or []),
                    "mechanism_signature": dict(observation.get("mechanism_signature") or {}),
                    "attribution_id": str(attribution.get("attribution_id") or ""),
                    "evidence_id": evidence_id,
                    "dataset": str(evidence.get("dataset") or ""),
                    "case_id": str(evidence.get("case_id") or ""),
                    "anchor_kind": str(attribution.get("anchor_kind") or ""),
                    "prompt_hash": prompt_hash,
                    "taxonomy_version": taxonomy_version,
                    "iteration": int(iteration),
                    "status": "untested" if candidate_eligible else "ineligible",
                    "candidate_eligible": candidate_eligible,
                    "role": str(attribution.get("role") or ""),
                    "matching_quality": str(attribution.get("matching_quality") or "not_available"),
                    "evidence_basis": str(attribution.get("evidence_basis") or ""),
                    "requirement_quote": str(attribution.get("requirement_quote") or ""),
                    "error_anchor": str(attribution.get("error_anchor") or ""),
                    "attribution": dict(attribution),
                    "evidence": dict(evidence),
                    "rejection_reasons": list(observation.get("candidate_exclusion_reasons") or []),
                    "lineage": {
                        "batch_id": int(observation.get("batch_id", 0)),
                        "source_attribution_id": str(attribution.get("attribution_id") or ""),
                    },
                }
                entries.append(existing)
                by_fingerprint[fingerprint] = existing
            else:
                existing["last_seen_iteration"] = int(iteration)
                existing["last_seen_attribution_id"] = str(attribution.get("attribution_id") or "")
                if existing.get("status") == "ineligible" and candidate_eligible:
                    existing["status"] = "untested"
    return memory


def mark_hypothesis_status(
    memory: dict[str, Any],
    *,
    prompt_hash: str,
    hypothesis_id: str,
    status: str,
    rejection_reasons: list[str] | None = None,
) -> dict[str, Any]:
    for item in memory.get("entries", []):
        if (
            isinstance(item, dict)
            and str(item.get("prompt_hash") or "") == prompt_hash
            and str(item.get("hypothesis_id") or "") == hypothesis_id
        ):
            item["status"] = status
            if rejection_reasons is not None:
                item["rejection_reasons"] = sorted(set(str(reason) for reason in rejection_reasons))
    return memory
