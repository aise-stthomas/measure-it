"""Record: run the system under test over the golden set and keep every call.

    uv run record.py --name baseline --runs 5                      # deliverable 5
    uv run record.py --name system --runs 5 --policy-in system     # deliverable 6
    uv run record.py --name try --runs 1 --provider fake           # no key, NOT a model
    uv run record.py --name baseline --runs 5 --limit 3            # three tickets, to test

Writes fixtures/<name>/run-<k>.jsonl, one line per call, as each call lands. It is
resumable: a call already in the file is never made again, so when you hit a rate limit
or the daily cap, rerun the same command later and it continues where it stopped.

Score from these files with score.py. Re-scoring costs nothing. Re-sampling costs quota
and gives you different data, so never delete a fixture to "clean up".
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from triage import DEFAULT_MODEL, triage

GOLDEN = Path("golden/golden.jsonl")
ACCOUNTS = Path("golden/accounts.json")
FIXTURES = Path("fixtures")


def load_golden() -> list[dict]:
    items = [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "duplicate id in golden.jsonl"
    return items


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--name", required=True, help="the condition being recorded, e.g. baseline")
    p.add_argument("--runs", type=int, default=1, help="passes over the whole suite")
    p.add_argument("--policy-in", choices=["user", "system"], default="user")
    p.add_argument("--provider", choices=["gemini", "fake"], default="gemini")
    p.add_argument("--limit", type=int, help="only the first N tickets")
    args = p.parse_args()

    items = load_golden()[: args.limit]
    accounts = json.loads(ACCOUNTS.read_text())
    out_dir = FIXTURES / args.name
    out_dir.mkdir(parents=True, exist_ok=True)

    for run in range(1, args.runs + 1):
        out = out_dir / f"run-{run}.jsonl"
        done = {json.loads(line)["id"] for line in out.read_text().splitlines()} if out.exists() else set()
        todo = [i for i in items if i["id"] not in done]
        print(f"{args.name} run {run}: {len(done)} recorded, {len(todo)} to go "
              f"({DEFAULT_MODEL} via {args.provider}, policy in the {args.policy_in} text)", flush=True)
        for item in todo:
            rec = triage(item["ticket"], accounts[item["account"]],
                         provider=args.provider, policy_in=args.policy_in)
            rec.update({"id": item["id"], "run": run, "condition": args.name})
            with out.open("a") as f:
                f.write(json.dumps(rec) + "\n")
            print(f"  {item['id']}  {rec['action']:9s} {'' if rec['refund_amount'] is None else rec['refund_amount']}", flush=True)


if __name__ == "__main__":
    main()
