# Measure it

An evaluation harness for one model call.

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
scorers that turn each output into pass or fail (one of them an LLM judge), and a report
per slice. A starting version of each is written. Extending them is the project.

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
uv run judge.py baseline                                     # JUDGE: the LLM judge reads each rationale, saves its verdicts
uv run score.py baseline                                     # SCORE: reads the saved files, never calls a model
```

Two of those steps call a model; the third never does. **Record once, score many
times.** `record.py` and `judge.py` write to `fixtures/<condition>/` as each call lands
and never repeat a call they already have: after a rate limit or the daily cap, rerun
the same command and it continues. `score.py` reads only those files, so rewriting a
scorer costs nothing and the data holds still. Fixtures are committed; your submission
is re-scored from them.

**The harness is a list of scorers.** In `harness/scorers.py`, each scorer is a function
`(item, output) -> True / False / None`, and `SCORERS` names them:

```python
SCORERS = {  # name: (function, what it checks)
    "action":    (score_action,    "the route is the one the policy requires"),
    "amount":    (score_amount,    "the amount never exceeds what the policy allows"),
    "format":    (score_format,    "the output parsed as a decision"),
    "rationale": (score_rationale, "the LLM judge says the reason holds up"),
}
```

The report applies every scorer in that list to every recorded output and files the
result under every slice tag. Adding a check is adding a function and a row.

## The files

```
system/          the system under test. Frozen: you measure it, you do not edit it.
  triage.py        render → sample → parse, and the policy_in option
  plumbing.py      rate-limit retries; the fake provider
harness/         the evaluation harness. Everything in here is yours.
  golden.py        loads golden/ and knows every slice an item belongs to
  fixtures.py      writes and reads fixtures/; never calls a model
  scorers.py       the scorers and the SCORERS registry
  judge.py         the LLM judge: a one-question rubric to start; YOURS to extend and validate
  report.py        per slice, per scorer, as counts; noise_floor is YOURS
record.py        CLI: runs the suite and saves every output
judge.py         CLI: runs the judge over recorded outputs and saves its verdicts
score.py         CLI: reads the fixtures and prints the report
golden/          golden.jsonl (the tickets) and accounts.json
fixtures/        every recorded output and verdict, by condition and run. Committed.
```
