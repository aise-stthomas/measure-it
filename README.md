# Measure it

Project 1 of AI Systems Engineering: build an evaluation harness for one model call.
**The assignment is [PROJECT.md](PROJECT.md).** This page is how to get running.

## Start

1. **Use this template** (the green button above) to create one **private** repository
   for your pair. Add your partner and the instructor as collaborators.
2. Clone it, then:

```bash
cp .env.example .env        # paste your own Gemini key; each of you has one
uv sync                     # or: python3 -m venv .venv && . .venv/bin/activate && pip install -e .
uv run record.py --name try --runs 1 --provider fake    # no key needed
uv run score.py try
rm -r fixtures/try
```

If that prints a table, the plumbing works. `--provider fake` is not a model: it checks
your harness and tells you nothing about the system.

## What is here

| File | What it is | Yours to change? |
|---|---|---|
| `triage.py` | The system under test: render, sample, parse. Frozen. | **No** |
| `plumbing.py` | Rate-limit retries and the fake provider. | No need |
| `golden/golden.jsonl` | The golden set. Three examples; you need 50–80. | **Yes** |
| `golden/accounts.json` | The account summaries your tickets refer to. | Yes |
| `record.py` | Runs the suite and keeps every live call in `fixtures/`. Resumable. | If you need to |
| `score.py` | Reads `fixtures/`, reports per slice. Only exact match on the action is written. | **Yes — this is the project** |
| `judge.py` | Empty. The judge and its validation. | **Yes** |

## The loop you will live in

```bash
uv run record.py --name baseline --runs 5                    # the unchanged system
uv run record.py --name system --runs 5 --policy-in system   # deliverable 6
uv run score.py baseline system                              # as often as you like: it never calls the model
```

`record.py` writes each call as it lands and never repeats a call it already has. When
you hit a rate limit or the daily cap, rerun the same command later, or with your
partner's key, and it continues where it stopped. Commit `fixtures/`: it is your data,
and your submission is re-scored from it.

Check your own limits at https://aistudio.google.com/rate-limit before you plan a
five-run sweep.

## What you hand in

Everything in the **Submit** section of [PROJECT.md](PROJECT.md), in this repository,
tagged `p1`. Add `report.md`, `blind-spots.md`, and `design.md` at the top level.
