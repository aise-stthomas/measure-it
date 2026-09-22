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

| File | What it is | Yours to change? |
|---|---|---|
| `triage.py` | **The system under test**: render, sample, parse. | **No** |
| `plumbing.py` | Rate-limit retries; the fake provider. | No need |
| `golden/golden.jsonl` | The golden set: tickets with the right answer, tagged by slice. | **Yes** |
| `golden/accounts.json` | The account summaries the tickets refer to. | Yes |
| `record.py` | Runs the suite; saves every call to `fixtures/`. | If you need to |
| `score.py` | The scorers and the per-slice report. Three scorers are written. | **Yes: this is the project** |
| `judge.py` | Empty. The model judge and its validation. | **Yes** |
