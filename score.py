"""Score: read the fixtures, never the model, and report per slice.

    uv run score.py baseline            # every run recorded under fixtures/baseline
    uv run score.py baseline system     # two conditions, one after the other

What is here is the smallest thing that runs: exact match on the action, one table per
run. Everything marked YOURS is the project. The order in the spec is a good order.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from record import FIXTURES, load_golden


def score_action(item: dict, rec: dict) -> bool:
    """Exact match. Malformed output is a failure, never dropped."""
    return rec["action"] == item["expected_action"]


def score_amount(item: dict, rec: dict) -> bool | None:
    """YOURS (deliverable 3). Is the proposed amount allowed?

    At minimum: not above item["max_refund"], not above what the action permits, and
    not a number that appears nowhere in the ticket or the account. Return None when no
    amount belongs in the output, so the report can say "not applicable" rather than
    "passed".
    """
    return None


def score_rationale(item: dict, rec: dict) -> dict | None:
    """YOURS (deliverables 3 and 4). A model judge with a written rubric.

    At minimum the rubric asks: does the rationale agree with the action that was
    actually taken, and does it state the policy correctly? The judge is a model call:
    record its outputs as fixtures too, and validate it against your own labels before
    you report a single number from it. Build it in judge.py.
    """
    return None


def passed(item: dict, rec: dict) -> bool:
    """One record passes when every scorer that applies says so."""
    checks = [score_action(item, rec), score_amount(item, rec)]
    return all(c for c in checks if c is not None)


def per_slice(items: dict[str, dict], records: list[dict]) -> dict[str, tuple[int, int]]:
    """slice tag -> (passed, total). Every tag on an item counts the item once."""
    table: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for rec in records:
        item = items[rec["id"]]
        ok = passed(item, rec)
        for tag in ["all"] + item["slices"] + (["ambiguous"] if item.get("ambiguous") else []):
            table[tag][0] += ok
            table[tag][1] += 1
    return {tag: (p, n) for tag, (p, n) in table.items()}


def noise_floor(runs: list[dict[str, tuple[int, int]]]) -> None:
    """YOURS (deliverable 5). Per slice: the pass rate of each run, and the spread.

    `runs` is one per_slice() table per recorded run of the same condition. Then
    deliverable 6: two conditions side by side, and for each slice one of three words:
    helped, hurt, or cannot tell.
    """


def main() -> None:
    items = {i["id"]: i for i in load_golden()}
    for name in sys.argv[1:] or ["baseline"]:
        tables = []
        for path in sorted((FIXTURES / name).glob("run-*.jsonl")):
            records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            records = [r for r in records if r["id"] in items]
            table = per_slice(items, records)
            tables.append(table)
            print(f"\n{name} / {path.stem}: {len(records)} records")
            for tag in sorted(table):
                p, n = table[tag]
                print(f"  {tag:32s} {p} of {n}")
        if not tables:
            print(f"no fixtures under {FIXTURES / name}; run record.py first")
        noise_floor(tables)


if __name__ == "__main__":
    main()
