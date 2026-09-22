# Lab: can you tell a change from a wobble?

In pairs. You build a small evaluation harness, run it against the triage system, and
see how much evidence fifteen tickets can give. The lab has the same shape as the
project, in miniature: **a dataset, then code, then a measurement.**

**The question.** The policy can be sent to the model in the same text as the ticket, or
as the system instruction. Does moving it help? You answer per slice, in one word:
**helped**, **hurt**, or **cannot tell**.

**What this lab shows.**

1. **The golden set is the specification.** Deciding the right answer is the hard part,
   and two people will not always agree.
2. **A harness is a list of scorers.** Adding a check is adding one function and one row.
3. **A judge is a model, so it gets measured too**, against your own labels.
4. **The number moves when nothing changes.** That wobble is the noise floor, and fifteen
   tickets cannot tell a change from it. That is why the project asks for fifty to eighty.

## Part 0: make it run

Do **Setup, once** in the [README](README.md). While your partner finishes, read
`system/triage.py`: it is the system under test, and you do not change it.

## Part 1: the dataset — write five tickets

`golden/golden.jsonl` has ten tickets. Add **five**, in the same format
(`golden/README.md` explains each field), one of each:

| Ticket | Expected action | Slice tags |
|---|---|---|
| a refund request **under \$50** | `refund` | `intent:refund`, `amount:under-50` |
| a refund request **between \$50 and \$200** | `hold` | `intent:refund`, `amount:50-to-200` |
| a refund request **over \$200** | `escalate` | `intent:refund`, `amount:over-200` |
| a question with **no money involved** | `answer` | `intent:question` |
| a ticket the two of you **disagree** on: put it **at a boundary** (a \$45 item plus \$8 shipping; "my \$52 order, but keep \$5 for the trouble") | your best call, and `"ambiguous": true` | whatever fits |

For each, fill in `policy` with the sentence of the policy that makes the answer right.
If you cannot quote one, keep the ticket and mark it ambiguous: that is a finding.

Then record the baseline:

```bash
uv run record.py --name baseline --runs 3     # 45 calls, saved under fixtures/baseline/
uv run score.py baseline
```

`score.py` prints one table per run: for each slice and each scorer, passed of total.

## Part 2: the code — add a scorer

Open `harness/scorers.py`. A scorer is a function `(item, output) -> True / False / None`,
and `SCORERS` is the list of them: a name, the function, and what it checks. The report
loop applies every scorer in that list to every recorded output. **Adding a check is
adding a function and a row.**

Add one. Suggested: `rationale_present`, which passes when the output has a rationale of
at most one sentence (say, 1 to 300 characters), since the policy asked for one. Then:

```bash
uv run score.py baseline       # re-scoring is free: nothing is re-recorded
```

Your new row appears in the table. Notice that you did not call the model.

## Part 3: the judge — and check it against yourself

The `rationale` scorer is different: the rationale is free text, so no rule can check it.
`harness/judge.py` is a **second model call** with a one-question rubric: *does the
rationale support the action that was actually taken?* Run it over the baseline:

```bash
uv run judge.py baseline       # 45 judge calls; verdicts saved as fixtures
uv run score.py baseline       # the rationale row now has numbers
```

Now measure the judge. Open `fixtures/baseline/run-1.jsonl`. **Each of you, alone,**
reads the fifteen rationales in it and answers the same question, yes or no, for each. Compare
with each other first; then compare with the judge's verdicts in
`fixtures/baseline/judge-run-1.jsonl`. Fill in the four counts:

| | judge: yes | judge: no |
|---|---|---|
| **you: yes** | ___ | ___ |
| **you: no** | ___ | ___ |

Where the judge and you disagree, read the rationale again. Who is right?

## Part 4: the change — measure the wobble, then give a verdict

For your largest slice, from the three baseline runs, write down the `action` pass count
in each run and **the noise floor**: highest rate minus lowest rate, in points.

Then one change:

```bash
uv run record.py --name system --runs 3 --policy-in system
uv run score.py baseline system
```

Same tickets, same model; the policy is now the system instruction. For **each slice**,
compare the three `baseline` runs with the three `system` runs and write one word:
**helped**, **hurt**, or **cannot tell**. The rule: a difference smaller than that slice's
noise floor is not evidence of anything.

Then, for your largest slice, the 95% interval on its baseline pass rate. With $x$ passes
of $n$:

$$\frac{\hat p + \frac{1.92}{n} \pm 1.96\sqrt{\frac{\hat p(1-\hat p)}{n} + \frac{0.96}{n^2}}}{1 + \frac{3.84}{n}}, \qquad \hat p = x/n$$

(4 of 6 gives 30% to 90%.) If the slice had zero failures, the rule of three: its true
failure rate could still be as high as $3/n$.

**If nothing wobbles.** A noise floor of zero means the model gave the same answer three
times on every ticket in that slice. That is a finding, not a failure: your tickets are
easy for it. To see the floor move, add one ticket that sits right at a boundary, such as
a \$48 item plus \$6 shipping, and rerun `record.py --name baseline --runs 3`. Only the
new ticket is recorded; the rest resume from the fixtures.

**Keep** the repository, with your tickets and fixtures in it. Project 1 continues there:
the same shape, at full size.

## If something breaks

| Symptom | What it is |
|---|---|
| `rate limited; sleeping` | Normal on the free tier; the run continues. If it stalls, rerun the same command: recording resumes where it stopped. |
| `refused: … quota` | The daily cap. Put your partner's key in `.env` and rerun the same command. |
| a slice you did not expect | A typo in a slice tag. Fix `golden.jsonl`; re-scoring is free. |
| `malformed` in the output | Not a bug. The model returned something that was not a decision; it counts as a failure. |
| the `rationale` row is missing | The judge has not been run on that condition yet: `uv run judge.py <condition>`. |
