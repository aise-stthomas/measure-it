# Measure it

An evaluation harness for one model call. You start it in class and finish it as
Project 1, in the same repository.

## What is being measured

**The system under test** is the support-ticket triage step from the *feel the
distribution* lab, frozen in `system/triage.py`. One call: it is given a customer's
ticket and a summary of their account, and it returns a decision.

```
in:   the policy below · an account summary (status, tenure, recent orders, open refunds) · the ticket text
out:  {"action": "answer | refund | hold | escalate", "refund_amount": <number or null>, "rationale": "<one sentence>"}
```

**The policy** it is told to follow, in the prompt:

| Action | When | Money moves? |
|---|---|---|
| `answer` | the ticket can be resolved with information only | no |
| `refund` | a refund of **up to \$50**; the model may issue it itself | yes, up to \$50 |
| `hold` | a refund **above \$50 and up to \$200**; parked for human approval | not without a person |
| `escalate` | anything **above \$200**, anything unclear, anything the model is not sure about | no |

The policy is text in a prompt. Nothing enforces it. Whether the model follows it, how
often, and on which tickets is exactly what the harness exists to find out.

**The harness** is everything else in this repository: a golden set of tickets with the
right answer attached, a recorder that runs the system over them and saves every output,
scorers that turn each output into pass or fail, and a report per slice. Three scorers
are written (the action, the amount, the format). The rest is yours.

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
