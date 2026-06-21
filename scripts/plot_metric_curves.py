#!/usr/bin/env python3
"""Plot train/test metric curves from APE run artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_METRICS = ("node_f1", "relation_f1", "plantuml_compilation_pass_rate")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_dirs(run_dir: Path) -> list[Path]:
    return [path for path in sorted(run_dir.glob("iteration_*")) if path.is_dir()]


def load_summary(path: Path) -> dict[str, float] | None:
    if not path.exists():
        return None
    payload = read_json(path)
    return {key: float(value) for key, value in payload.items() if isinstance(value, (int, float))}


def build_rows(run_dir: Path, metrics: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for iter_dir in iter_dirs(run_dir):
        iteration = int(iter_dir.name.rsplit("_", 1)[-1])
        train_summary = load_summary(iter_dir / "evaluation" / "analysis_summary.json")
        batch_gate_summaries = [
            summary
            for batch_dir in sorted((iter_dir / "train_batches").glob("batch_*"))
            for summary in [load_summary(batch_dir / "gate" / "candidate_summary.json")]
            if summary is not None
        ]
        gate_summary = batch_gate_summaries[-1] if batch_gate_summaries else load_summary(iter_dir / "evaluation" / "gate_candidate_summary.json")
        iteration_test_summary = load_summary(iter_dir / "held_out_test" / "summary.json")

        for split, summary in (
            ("train_epoch", train_summary),
            ("gate_candidate", gate_summary),
            ("iteration_test", iteration_test_summary),
        ):
            if summary is None:
                continue
            row: dict[str, Any] = {"iteration": iteration, "split": split}
            for metric in metrics:
                row[metric] = summary.get(metric)
            rows.append(row)

    final_test_summary = load_summary(run_dir / "test" / "summary.json")
    if final_test_summary is not None:
        final_iteration = max((int(path.name.rsplit("_", 1)[-1]) for path in iter_dirs(run_dir)), default=0)
        row = {"iteration": final_iteration, "split": "final_test"}
        for metric in metrics:
            row[metric] = final_test_summary.get(metric)
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], metrics: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["iteration", "split", *metrics])
        writer.writeheader()
        writer.writerows(rows)


def plot(rows: list[dict[str, Any]], metrics: list[str], output_path: Path) -> None:
    import matplotlib.pyplot as plt

    splits = ("train_epoch", "gate_candidate", "iteration_test", "final_test")
    labels = {
        "train_epoch": "train epoch aggregate",
        "gate_candidate": "last batch gate candidate",
        "iteration_test": "iteration held-out test",
        "final_test": "final held-out test",
    }
    styles = {
        "train_epoch": {"marker": "o", "linestyle": "-"},
        "gate_candidate": {"marker": "s", "linestyle": "--"},
        "iteration_test": {"marker": "^", "linestyle": "-"},
        "final_test": {"marker": "X", "linestyle": "None"},
    }

    fig, axes = plt.subplots(len(metrics), 1, figsize=(10, max(3, 2.8 * len(metrics))), sharex=True)
    if len(metrics) == 1:
        axes = [axes]

    for ax, metric in zip(axes, metrics):
        for split in splits:
            points = [
                (int(row["iteration"]), row.get(metric))
                for row in rows
                if row.get("split") == split and isinstance(row.get(metric), (int, float))
            ]
            if not points:
                continue
            points.sort()
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            ax.plot(xs, ys, label=labels[split], **styles[split])
        ax.set_ylabel(metric)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0.0)
        if metric.endswith("_rate") or metric.endswith("_f1"):
            ax.set_ylim(0.0, 1.0)

    axes[-1].set_xlabel("iteration")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, legend_labels, loc="upper center", ncol=2)
        fig.tight_layout(rect=(0, 0, 1, 0.92))
    else:
        fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot metric curves from an APE prompt run directory.")
    parser.add_argument("run_dir", type=Path, help="Run directory containing iteration_* artifacts")
    parser.add_argument("--metrics", nargs="+", default=list(DEFAULT_METRICS), help="Metric keys to plot")
    parser.add_argument("--output", type=Path, default=None, help="Output image path; defaults to RUN_DIR/metric_curves.png")
    parser.add_argument("--csv", type=Path, default=None, help="Output CSV path; defaults to RUN_DIR/metric_curves.csv")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
    output_path = args.output.resolve() if args.output else run_dir / "metric_curves.png"
    csv_path = args.csv.resolve() if args.csv else run_dir / "metric_curves.csv"

    metrics = [str(metric) for metric in args.metrics]
    rows = build_rows(run_dir, metrics)
    if not rows:
        raise ValueError(f"No metric summaries found under {run_dir}")
    write_csv(csv_path, rows, metrics)
    plot(rows, metrics, output_path)
    print(f"[plot] wrote {output_path}")
    print(f"[plot] wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
