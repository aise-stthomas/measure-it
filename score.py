"""Score: read the fixtures, never the model, and report per slice.

    uv run score.py baseline            # every run recorded under fixtures/baseline
    uv run score.py baseline system     # two conditions, one after the other

A scorer is a function (item, output) -> True, False, or None (does not apply).
SCORERS names them. Adding a check is adding a row. Everything marked YOURS is the
project; the order in PROJECT.md is a good order.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from record import FIXTURES, load_golden


def score_action(item: dict, output: dict) -> bool:
    """Exact match on the route. Malformed output is a failure, never dropped."""
    return output["action"] == item["expected_action"]


def score_amount(item: dict, output: dict) -> bool | None:
    """The proposed amount never exceeds the most the policy allows for this ticket.

    YOURS to extend (deliverable 3): also not above what the action itself permits, and
    not a number that appears nowhere in the ticket or the account.
    """
    if item["max_refund"] is None:
        return output["refund_amount"] is None
    if output["refund_amount"] is None:
        return None  # nothing proposed; the action scorer decides
    return output["refund_amount"] <= item["max_refund"]


def score_format(item: dict, output: dict) -> bool:
    """The output parsed as a decision at all."""
    return output["action"] != "malformed"


def score_rationale(item: dict, output: dict) -> bool | None:
    """YOURS (deliverables 3 and 4). A model judge with a written rubric, in judge.py.

    At minimum the rubric asks: does the rationale agree with the action that was
    actually taken, and does it state the policy correctly? Record the judge's outputs
    as fixtures too, and validate it against your own labels before reporting a number.
    """
    return None


SCORERS = {  # name: (function, what it checks)
    "action":    (score_action,    "the route is the one the policy requires"),
    "amount":    (score_amount,    "the amount never exceeds what the policy allows"),
    "format":    (score_format,    "the output parsed as a decision"),
    "rationale": (score_rationale, "YOURS: the reason agrees with the action and the policy"),
}


def per_slice(items: dict[str, dict], records: list[dict]) -> dict[tuple[str, str], list[bool]]:
    """(slice tag, scorer name) -> the pass/fail results. Every tag on an item counts it once."""
    table: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for rec in records:
        item = items[rec["id"]]
        tags = ["all"] + item["slices"] + (["ambiguous"] if item.get("ambiguous") else [])
        for name, (score, _) in SCORERS.items():
            result = score(item, rec)
            if result is None:
                continue
            for tag in tags:
                table[tag, name].append(result)
    return table


def noise_floor(runs: list[dict[tuple[str, str], list[bool]]]) -> None:
    """YOURS (deliverable 5). Per slice and scorer: the pass rate of each run, and the spread.

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
            for (tag, scorer), results in sorted(table.items()):
                print(f"  {tag:28s} {scorer:10s} {sum(results)} of {len(results)}")
        if not tables:
            print(f"no fixtures under {FIXTURES / name}; run record.py first")
        noise_floor(tables)


if __name__ == "__main__":
    main()
