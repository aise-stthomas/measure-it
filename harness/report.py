"""The report: per slice, per scorer, as counts. Read against the requirement."""
from __future__ import annotations

from collections import defaultdict

from .golden import tags
from .scorers import SCORERS

Table = dict[tuple[str, str], list[bool]]  # (slice tag, scorer name) -> results


def per_slice(items: dict[str, dict], records: list[dict]) -> Table:
    """Apply every scorer to every recorded output and file the result under every slice tag."""
    table: Table = defaultdict(list)
    for rec in records:
        item = items[rec["id"]]
        for name, (score, _) in SCORERS.items():
            result = score(item, rec)
            if result is None:
                continue
            for tag in tags(item):
                table[tag, name].append(result)
    return table


def print_table(title: str, table: Table) -> None:
    print(f"\n{title}")
    for (tag, scorer), results in sorted(table.items()):
        print(f"  {tag:28s} {scorer:10s} {sum(results)} of {len(results)}")


def noise_floor(runs: list[Table]) -> None:
    """YOURS (deliverable 2.3). Per slice and scorer: the pass rate of each run, and the spread.

    `runs` is one per_slice() table per recorded run of the same condition. Then
    the question in 3.2: two conditions side by side, and for each slice one of three words:
    helped, hurt, or cannot tell.
    """
