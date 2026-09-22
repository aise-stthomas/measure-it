"""Record: run the system under test over the golden set and keep every call.

    uv run record.py --name baseline --runs 5                      # deliverable 5
    uv run record.py --name system --runs 5 --policy-in system     # deliverable 6
    uv run record.py --name try --runs 1 --provider fake           # no key, NOT a model
    uv run record.py --name baseline --runs 5 --limit 3            # three tickets, to test

Writes fixtures/<name>/run-<k>.jsonl, one line per call, as each call lands. Resumable:
a call already in the file is never made again, so after a rate limit or the daily cap,
rerun the same command and it continues where it stopped.
"""
from __future__ import annotations

import argparse

from harness import fixtures, golden
from system import DEFAULT_MODEL, triage


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--name", required=True, help="the condition being recorded, e.g. baseline")
    p.add_argument("--runs", type=int, default=1, help="passes over the whole suite")
    p.add_argument("--policy-in", choices=["user", "system"], default="user")
    p.add_argument("--provider", choices=["gemini", "fake"], default="gemini")
    p.add_argument("--limit", type=int, help="only the first N tickets")
    args = p.parse_args()

    items = golden.load_golden()[: args.limit]
    accounts = golden.load_accounts()
    for run in range(1, args.runs + 1):
        path = fixtures.run_path(args.name, run)
        done = fixtures.recorded_ids(path)
        todo = [i for i in items if i["id"] not in done]
        print(f"{args.name} run {run}: {len(done)} recorded, {len(todo)} to go "
              f"({DEFAULT_MODEL} via {args.provider}, policy in the {args.policy_in} text)", flush=True)
        for item in todo:
            rec = triage(item["ticket"], accounts[item["account"]],
                         provider=args.provider, policy_in=args.policy_in)
            rec.update({"id": item["id"], "run": run, "condition": args.name})
            fixtures.append(path, rec)
            print(f"  {item['id']}  {rec['action']:9s} {'' if rec['refund_amount'] is None else rec['refund_amount']}", flush=True)


if __name__ == "__main__":
    main()
