# Lab: can you tell a change from a wobble?

In pairs. You build the smallest evaluation harness that can answer a real question,
run it against the triage system, and see how much evidence eight tickets can give.

**The question.** The policy can be sent to the model in the same text as the ticket, or
as the system instruction. Does moving it help? You answer per slice, in one word:
**helped**, **hurt**, or **cannot tell**.

**What this lab shows.** Three things, in order:

1. **The golden set is the specification.** Deciding the right answer for a ticket is the
   hard part, and two people will not always agree.
2. **The number moves when nothing changes.** Run the same tickets three times and the
   pass rate wobbles. That wobble is the noise floor.
3. **Eight tickets cannot tell a change from a wobble.** On most slices the honest
   verdict is "cannot tell." That is why the project asks for fifty to eighty.

## Part 0: make it run

Do **Setup, once** in the [README](README.md). While your partner finishes, read
`system/triage.py`: it is the system under test, and you do not change it.

## Part 1: write five tickets

`golden/golden.jsonl` has three tickets. Add **five**, in the same format
(`golden/README.md` explains each field), one of each:

| Ticket | Expected action | Slice tags |
|---|---|---|
| a refund request **under \$50** | `refund` | `intent:refund`, `amount:under-50` |
| a refund request **between \$50 and \$200** | `hold` | `intent:refund`, `amount:50-to-200` |
| a refund request **over \$200** | `escalate` | `intent:refund`, `amount:over-200` |
| a question with **no money involved** | `answer` | `intent:question` |
| a ticket the two of you **disagree** on | your best call, and `"ambiguous": true` | whatever fits |

For each, fill in `policy` with the sentence of the policy that makes the answer right.
If you cannot quote one, keep the ticket and mark it ambiguous: that is a finding.

> You have just written a specification. Eight examples with the right answer attached
> is the whole definition of "correct" this harness will ever have.

## Part 2: measure the wobble

```bash
uv run record.py --name baseline --runs 3     # 24 calls
uv run score.py baseline
```

`score.py` prints one table per run: for each slice and each scorer, passed of total.
Use the `action` rows. For your largest slice, write down:

- the pass count in each run: ___ / ___ / ___ of ___
- **the noise floor**: highest rate minus lowest rate = ___ points

## Part 3: make one change, and give a verdict

```bash
uv run record.py --name system --runs 3 --policy-in system
uv run score.py baseline system
```

Same tickets, same model; the policy is now the system instruction. For **each slice**,
compare the three `baseline` runs with the three `system` runs and write one word:
**helped**, **hurt**, or **cannot tell**. The rule: a difference smaller than that
slice's noise floor is not evidence of anything.

Then, for your largest slice, the 95% interval on its baseline pass rate. With $x$
passes of $n$:

$$\frac{\hat p + \frac{1.92}{n} \pm 1.96\sqrt{\frac{\hat p(1-\hat p)}{n} + \frac{0.96}{n^2}}}{1 + \frac{3.84}{n}}, \qquad \hat p = x/n$$

(4 of 6 gives 30% to 90%.) If the slice had zero failures, the rule of three: its true
failure rate could still be as high as $3/n$.

## Part 4: write it down

Create `lab.md` in your repository:

1. The noise floor on one slice, with the three counts behind it.
2. Your verdict per slice, with the numbers each rests on.
3. The 95% interval on your largest slice, and one sentence: how many tickets would that
   slice need before you would believe a 10-point improvement?
4. The ticket you disagreed on, and what the disagreement was about.

Commit and push. This repository continues as Project 1.

## If something breaks

| Symptom | What it is |
|---|---|
| `rate limited; sleeping` | Normal on the free tier; the run continues. If it stalls, rerun the same command: recording resumes where it stopped. |
| `refused: … quota` | The daily cap. Put your partner's key in `.env` and rerun the same command. |
| a slice you did not expect | A typo in a slice tag. Fix `golden.jsonl`; re-scoring is free. |
| `malformed` in the output | Not a bug. The model returned something that was not a decision; it counts as a failure. |
