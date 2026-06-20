# Prompt Runs By Dataset

This directory groups held-out test runs by the dataset detected from each run's test cases.

Each dataset subdirectory contains Windows directory junctions pointing back to the original directories under prompt_runs; the original logs are not moved or copied.

Datasets: bp, fsd, lmc, pure, rac, us.

Generated files:
- uns_index.csv: classified single-dataset held-out test runs and metrics when available.
- skipped_runs.csv: train-only, mixed, diagnostic, or unknown runs not placed in the six dataset folders.
