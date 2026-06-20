"""Diagnose parser behavior on LATO gold PlantUML files.

This script is read-only: it scans prompt_datasets/lato, parses gold PlantUML
with metrics.extract_activity_graph, and prints aggregate risk signals.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from metrics import _parse_relation, extract_activity_graph  # noqa: E402


PATTERNS = {
    "elseif": re.compile(r"\b(?:elseif|else\s+if)\b", re.IGNORECASE),
    "switch": re.compile(r"\bswitch\s*\(", re.IGNORECASE),
    "case": re.compile(r"\bcase\s*\(", re.IGNORECASE),
    "fork": re.compile(r"(?m)^\s*fork\b", re.IGNORECASE),
    "fork_end_variant": re.compile(r"\bfork\s+end\b", re.IGNORECASE),
    "note": re.compile(r"(?m)^\s*note\b", re.IGNORECASE),
    "inline_note": re.compile(r"(?m)^\s*note\s+\w+\s*:", re.IGNORECASE),
    "styled_arrow": re.compile(r"-\[[^\]]+\]-*>", re.IGNORECASE),
    "shorthand_arrow": re.compile(r"(?m)^\s*-+>\s*[^;\n]+;?\s*$", re.IGNORECASE),
    "repeat": re.compile(r"(?m)^\s*repeat\b", re.IGNORECASE),
    "while": re.compile(r"(?m)^\s*while\s*\(", re.IGNORECASE),
}

CONTROL_LABEL = re.compile(
    r"^\s*(@startuml|@enduml|skinparam\b.*|title\b.*|note\b.*|end note|partition\b.*|group\b.*|"
    r"fork|fork again|end fork|fork end|endfork|endif|end if|else\b.*|elseif\b.*|else if\b.*|"
    r"while\s*\(.*|endwhile|repeat while\b.*|switch\s*\(.*|case\s*\(.*|endswitch|"
    r"start|stop|end|yes|no)\s*$",
    re.IGNORECASE,
)
ARROW_OR_STYLE = re.compile(r"->|-\[|\[#", re.IGNORECASE)

LEGIT_SUBSTRINGS = (
    "start-stop",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose parser output on LATO gold PlantUML.")
    parser.add_argument(
        "--datasets-dir",
        type=Path,
        default=ROOT / "prompt_datasets" / "lato",
        help="Directory containing LATO *.jsonl files.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of largest relation-count cases and suspicious examples to print.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for report.md, summary.json, and cases.jsonl. Defaults to prompt_runs/<timestamp>__parser-diagnostics__gold.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print to stdout only and do not create diagnostic artifacts.",
    )
    return parser.parse_args()


def case_id_for(path: Path, row: dict, index: int) -> str:
    return str(row.get("case_id") or f"{path.stem}-{index:04d}")


def gold_plantuml(row: dict) -> str:
    return str(row.get("plantuml") or row.get("gold_plantuml") or "")


def is_suspicious_label(label: str) -> bool:
    if any(text in label for text in LEGIT_SUBSTRINGS):
        return False
    return bool(CONTROL_LABEL.search(label) or ARROW_OR_STYLE.search(label))


def make_output_dir(explicit_dir: Path | None) -> Path:
    if explicit_dir is not None:
        return explicit_dir.resolve()
    stamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    return ROOT / "prompt_runs" / f"{stamp}__parser-diagnostics__gold"


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def render_report(summary: dict, case_records: list[dict], top: int) -> str:
    lines = [
        "# Gold Parser Diagnostics",
        "",
        f"- datasets_dir: `{summary['datasets_dir']}`",
        f"- total_cases: {summary['total_cases']}",
        "",
        "## Dataset Stats",
        "",
    ]
    for dataset, stats in sorted(summary["datasets"].items()):
        lines.append(f"### {dataset}")
        lines.append("")
        lines.append(f"- cases: {stats['cases']}")
        lines.append(f"- node range/avg: {stats['node_min']} - {stats['node_max']} / {stats['node_avg']}")
        lines.append(f"- relation range/avg: {stats['relation_min']} - {stats['relation_max']} / {stats['relation_avg']}")
        lines.append(f"- duplicate cases: nodes={stats['node_dup_cases']}, relations={stats['relation_dup_cases']}")
        lines.append(f"- suspicious_cases: {stats['suspicious_cases']}")
        lines.append(f"- syntax case counts: `{stats['syntax']}`")
        lines.append("")

    lines.extend(["## Top Relation Count", ""])
    for item in summary["top_relation_count"][:top]:
        lines.append(f"- {item['case_id']}: nodes={item['node_count']}, relations={item['relation_count']}")

    lines.extend(["", "## Suspicious Examples", ""])
    suspicious = [record for record in case_records if record["suspicious_nodes"] or record["suspicious_relation_parts"]]
    if not suspicious:
        lines.append("- None")
    else:
        for record in suspicious[:top]:
            lines.append(f"- {record['case_id']}: nodes={record['suspicious_nodes'][:5]}, relations={record['suspicious_relation_parts'][:5]}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    datasets_dir = args.datasets_dir.resolve()
    if not datasets_dir.exists():
        print(f"Dataset directory not found: {datasets_dir}", file=sys.stderr)
        return 2

    rows: list[tuple[str, str, str]] = []
    for path in sorted(datasets_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for index, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                rows.append((path.stem, case_id_for(path, row, index), gold_plantuml(row)))

    dataset_stats: dict[str, dict] = {}
    suspicious: list[dict] = []
    largest: list[tuple[int, int, str]] = []
    case_records: list[dict] = []

    for dataset, case_id, uml in rows:
        graph = extract_activity_graph(uml)
        stats = dataset_stats.setdefault(
            dataset,
            {
                "cases": 0,
                "nodes": [],
                "relations": [],
                "syntax": Counter(),
                "node_dup_cases": 0,
                "relation_dup_cases": 0,
                "suspicious_cases": 0,
            },
        )

        stats["cases"] += 1
        stats["nodes"].append(len(graph.nodes))
        stats["relations"].append(len(graph.relations))

        syntax_hits: dict[str, int] = {}
        for name, pattern in PATTERNS.items():
            count = len(pattern.findall(uml))
            if count:
                stats["syntax"][name] += 1
                syntax_hits[name] = count

        node_dups = {key: value for key, value in Counter(graph.nodes).items() if value > 1}
        relation_dups = {key: value for key, value in Counter(graph.relations).items() if value > 1}
        if node_dups:
            stats["node_dup_cases"] += 1
        if relation_dups:
            stats["relation_dup_cases"] += 1

        bad_nodes = [node for node in graph.nodes if is_suspicious_label(node)]
        bad_relation_parts = []
        for relation in graph.relations:
            parsed = _parse_relation(relation)
            if not parsed:
                bad_relation_parts.append((relation, "unparseable"))
                continue
            for key, value in {"source": parsed.source, "target": parsed.target}.items():
                if is_suspicious_label(value):
                    bad_relation_parts.append((relation, f"{key}={value}"))

        relation_kind_counts = Counter()
        for relation in graph.relations:
            parsed = _parse_relation(relation)
            if parsed:
                relation_kind_counts[parsed.kind or "sequential"] += 1

        if bad_nodes or bad_relation_parts:
            stats["suspicious_cases"] += 1
            suspicious.append(
                {
                    "case_id": case_id,
                    "bad_nodes": bad_nodes[:5],
                    "bad_rel_parts": bad_relation_parts[:5],
                }
            )

        largest.append((len(graph.relations), len(graph.nodes), case_id))
        case_records.append(
            {
                "dataset": dataset,
                "case_id": case_id,
                "node_count": len(graph.nodes),
                "relation_count": len(graph.relations),
                "syntax_hits": syntax_hits,
                "node_duplicates": node_dups,
                "relation_duplicates": relation_dups,
                "suspicious_nodes": bad_nodes,
                "suspicious_relation_parts": bad_relation_parts,
                "relation_kind_counts": dict(relation_kind_counts),
            }
        )

    summary_datasets = {}
    for dataset, stats in sorted(dataset_stats.items()):
        nodes = stats["nodes"]
        relations = stats["relations"]
        summary_datasets[dataset] = {
            "cases": stats["cases"],
            "node_min": min(nodes),
            "node_max": max(nodes),
            "node_avg": round(sum(nodes) / len(nodes), 2),
            "relation_min": min(relations),
            "relation_max": max(relations),
            "relation_avg": round(sum(relations) / len(relations), 2),
            "node_dup_cases": stats["node_dup_cases"],
            "relation_dup_cases": stats["relation_dup_cases"],
            "suspicious_cases": stats["suspicious_cases"],
            "syntax": dict(stats["syntax"]),
        }

    top_relation_count = [
        {"case_id": case_id, "node_count": node_count, "relation_count": relation_count}
        for relation_count, node_count, case_id in sorted(largest, reverse=True)
    ]
    summary = {
        "datasets_dir": str(datasets_dir),
        "total_cases": len(rows),
        "datasets": summary_datasets,
        "top_relation_count": top_relation_count[: args.top],
        "suspicious_examples": suspicious[: args.top],
    }

    if not args.no_write:
        output_dir = make_output_dir(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(output_dir / "summary.json", summary)
        write_jsonl(output_dir / "cases.jsonl", case_records)
        (output_dir / "report.md").write_text(render_report(summary, case_records, args.top), encoding="utf-8")
        summary["output_dir"] = str(output_dir)
        write_json(output_dir / "summary.json", summary)

    print(f"DATASETS_DIR {datasets_dir}")
    print(f"TOTAL_CASES {len(rows)}")
    if not args.no_write:
        print(f"OUTPUT_DIR {summary['output_dir']}")

    print("\nDATASET_STATS")
    for dataset, stats in sorted(summary_datasets.items()):
        print(dataset, stats)

    print("\nTOP_RELATION_COUNT")
    for item in top_relation_count[: args.top]:
        print(item["case_id"], f"nodes={item['node_count']}", f"relations={item['relation_count']}")

    print("\nSUSPICIOUS_EXAMPLES")
    for item in suspicious[: args.top]:
        print(item)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
