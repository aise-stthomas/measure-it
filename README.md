# Measure it

An evaluation harness for one model call: the support-ticket triage step from the
*feel the distribution* lab. You start it in class and finish it as Project 1, in the
same repository.

| | |
|---|---|
| **In class** | [LAB.md](LAB.md) — *Can you tell a change from a wobble?* |
| **The project** | [PROJECT.md](PROJECT.md) — what to deliver, how it is graded |
| **The golden set format** | [golden/README.md](golden/README.md) |

## Setup, once

1. On GitHub, **Use this template** → one **private** repository for your pair. Add
   your partner and the instructor as collaborators.
2. Clone it, then:

```bash
cp .env.example .env        # paste your own Gemini key; each of you has one
uv sync                     # or: python3 -m venv .venv && . .venv/bin/activate && pip install -e .
uv run record.py --name try --runs 1 --provider fake    # no key needed
uv run score.py try
rm -r fixtures/try          # clean up: the fake provider's output is not data
```

If `score.py` printed a table, the plumbing works. `--provider fake` is not a model; it
checks the harness and tells you nothing about the system.

## The loop

```bash
uv run record.py --name baseline --runs 5                    # RECORD: calls the model, saves every output
uv run record.py --name system --runs 5 --policy-in system   # a second condition
uv run score.py baseline system                              # SCORE: reads the saved outputs, never calls the model
```

**Record once, score many times.** `record.py` writes every model output to
`fixtures/<condition>/run-<k>.jsonl` as it lands, and never repeats a call it already
has: after a rate limit or the daily cap, rerun the same command and it continues.
`score.py` reads only those files, so rewriting a scorer costs nothing and the data holds
still. Fixtures are committed; your submission is re-scored from them.

## The files

```
system/          the system under test. Frozen: you measure it, you do not edit it.
  triage.py        render → sample → parse, and the policy_in option
  plumbing.py      rate-limit retries; the fake provider
harness/         the evaluation harness. Everything in here is yours.
  golden.py        loads golden/ and knows every slice an item belongs to
  fixtures.py      writes and reads fixtures/; never calls the model
  scorers.py       the scorers and the SCORERS registry: three written, rationale YOURS
  report.py        per slice, per scorer, as counts; noise_floor is YOURS
  judge.py         empty: the model judge and its validation
record.py        CLI: runs the suite and saves every call
score.py         CLI: reads the fixtures and prints the report
golden/          golden.jsonl (the tickets) and accounts.json
fixtures/        every recorded model output, by condition and run. Committed.
```
