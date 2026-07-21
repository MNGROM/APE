"""Export traceable mechanism evidence from a legacy prompt run."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.mechanism_clustering import export_legacy_mechanism_evidence
from config import DEFAULT_RUNS_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_run", type=Path)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    args = parser.parse_args()
    audit_dir, summary = export_legacy_mechanism_evidence(args.source_run, args.runs_dir)
    print(f"[mechanism-audit] output={audit_dir}")
    print(
        "[mechanism-audit] "
        f"patterns={summary['source_pattern_count']}, "
        f"valid={summary['valid_reference_count']}, "
        f"invalid={summary['invalid_reference_count']}"
    )


if __name__ == "__main__":
    main()
