"""Score: read the fixtures, never the model, and report per slice and per scorer.

    uv run score.py baseline            # every run recorded under fixtures/baseline
    uv run score.py baseline system     # two conditions, one after the other

The scorers are in harness/scorers.py and the report in harness/report.py.
"""
from __future__ import annotations

import sys

from harness import fixtures, golden, report


def main() -> None:
    items = {i["id"]: i for i in golden.load_golden()}
    for name in sys.argv[1:] or ["baseline"]:
        tables = []
        for run_name, records in fixtures.runs(name):
            records = [r for r in records if r["id"] in items]
            table = report.per_slice(items, records)
            tables.append(table)
            report.print_table(f"{name} / {run_name}: {len(records)} records", table)
        if not tables:
            print(f"no fixtures under {fixtures.FIXTURES / name}; run record.py first")
        report.noise_floor(tables)


if __name__ == "__main__":
    main()
