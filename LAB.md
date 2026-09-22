# Lab: can you tell a change from a wobble?

In pairs. You will build the smallest evaluation harness that can answer a real
question, run it against the triage system from the *feel the distribution* lab,
and find out how much evidence eight tickets can give you. The repository you make
here is where Project 1 continues.

**The question.** The policy can be sent to the model two ways: in the same text as
the ticket, or as the system instruction. Does moving it help? You will answer that
per slice, in one of three words: *helped*, *hurt*, or *cannot tell*.

## Part 0: make the harness run

Do **Setup, once** in the [README](README.md): the template, the key, `uv sync`, and the
fake-provider check. Then read `system/triage.py` while your partner finishes: it is the system
under test, and you do not change it.

## Part 1: write five tickets

Open `golden/golden.jsonl`. Three tickets are there. Add **five** of your own, in the
same format (`golden/README.md` explains each field). Cover these, one each:

| Your ticket | The policy says | Slice tags to use |
|---|---|---|
| a refund request **under \$50** | `refund` | `intent:refund`, `amount:under-50` |
| a refund request **between \$50 and \$200** | `hold` | `intent:refund`, `amount:50-to-200` |
| a refund request **over \$200** | `escalate` | `intent:refund`, `amount:over-200` |
| a question with **no money involved** | `answer` | `intent:question` |
| a ticket where the two of you **disagree** on the right answer | your best call, with `"ambiguous": true` | whatever fits |

For every ticket, fill in `policy` with the sentence of the policy that makes your
answer right. If you cannot quote one, that is a finding: write the ticket anyway and
mark it ambiguous.

**Before you go on:** you have just written a specification. Eight examples with the
right answer attached is the whole definition of "correct" your harness will ever have.
Notice how long the fifth ticket took.

## Part 2: record the baseline, three times

```bash
uv run record.py --name baseline --runs 3
uv run score.py baseline
```

Twenty-four calls. `score.py` prints one table per run: for each slice and each scorer, passed of total. Use the `action` rows.

Write down, for the slice `intent:refund` (or the largest slice you have):

- the `action` pass count in each of the three runs: ___ / ___ / ___ of ___
- **the noise floor** on that slice: highest rate minus lowest rate = ___ points

That number is how much your measurement moves when nothing changes.

## Part 3: make one change, and judge it

```bash
uv run record.py --name system --runs 3 --policy-in system
uv run score.py baseline system
```

Same tickets, same model, one change: the policy is now the system instruction.

For **each slice**, compare the three baseline runs with the three `system` runs and
write one word: **helped**, **hurt**, or **cannot tell**. The rule from the lecture: a
difference smaller than the noise floor on that slice is not evidence of anything.

Then one more line, for your largest slice: the 95% interval on its baseline pass
rate, from the formula on the slide (or, if it had zero failures, the rule of three:
the true failure rate could still be as high as 3 / n). How wide is it?

## Part 4: write it down

In your repository, create `lab.md` with:

1. The noise floor on one slice, with the three counts behind it.
2. Your verdict per slice, and the numbers each verdict rests on.
3. One sentence: how many tickets would you need on that slice before you would
   believe a 10-point improvement? (Use the interval you just computed as a guide.)
4. The ticket the two of you disagreed on, and what the disagreement was about.

Commit and push. **That file, and this repository, are the start of Project 1.**

## What you should have seen

On eight tickets, most slices come out **cannot tell**: a slice of two or three
tickets moves by 33 to 50 points between runs on its own, so no change can show
through. That is not a failure of your harness. It is the reason Project 1 asks for
fifty to eighty tickets, five runs, and counts beside every percentage.

## If something breaks

| Symptom | What it is |
|---|---|
| `rate limited; sleeping` | Normal on the free tier; the run continues. If it stalls, rerun the same command: recording resumes where it stopped. |
| `refused: … quota` | The daily cap. Switch to your partner's key in `.env` and rerun the same command. |
| `score.py` shows a slice you did not expect | A typo in a slice tag. Fix it in `golden.jsonl`; re-scoring is free. |
| `malformed` in the output | Not a bug. The model returned something that was not a decision; it is counted as a failure. |
