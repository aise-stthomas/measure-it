# P1 — Measure it

**The assignment:** build an evaluation harness for the triage system in this repository, and
use it to answer one question with evidence: does sending the policy as the system
instruction, instead of beside the ticket, help? Your answer is per slice, with a noise
floor, with a judge you validated, and with an honest list of what the harness cannot
see.

The harness is the AI system's test suite, its specification, and its release gate at
once. Everything you ship later in the course is gated on one. You do not need to know
anything about agents for this project: the system under test is one model call that
makes one consequential decision.

## Deliverables

Three things: a dataset, code, and a write-up.

### 1. The golden dataset — `golden/golden.jsonl`

50–80 tickets you write, each with the action the policy requires, the most the refund
may be, and the sentence of the policy that makes that the right answer. Realistic
tickets across every intent the policy covers, plus edge and adversarial items. A ticket
the two of you cannot agree on stays in, tagged `ambiguous`.

**Slices are tags on the tickets**, not code: the report groups by every tag it finds.
Tag so that these slices exist, at minimum: by intent; by amount relative to the caps
(well under, near, over \$50, over \$200); by whether the ticket contains text addressed
to the model; and one slice of your own that you expect to fail.

### 2. Code — `harness/`

**2.1 Scorers** (`harness/scorers.py`). Three are written: `action` (exact match),
`amount` (within the cap), `format` (it parsed). You extend `amount` so it also fails a
number that appears nowhere in the ticket or the account. Every scorer returns pass,
fail, or "does not apply"; malformed output is a failure, never dropped.

**2.2 The LLM judge** (`harness/judge.py`, wired into `score_rationale`). The rationale
is free text, so no rule can score it. Its scorer is a second model call with a written
rubric: the rubric in the system instruction, the rationale with its action and the
policy in the user text, yes/no questions out. At minimum the rubric asks: does the
rationale agree with the action taken, and does it state the policy and the arithmetic
correctly? Both fail in this system's output: one rationale ends "choosing to hold since
it exceeds my limit" on a `refund` of \$52.99; another says the total "is under \$50" when
it is \$52.99. The judge's own calls are recorded as fixtures too.

**2.3 The noise floor** (`noise_floor` in `harness/report.py`). Given the tables from
several runs of one condition, the pass rate per slice per run and the spread; given two
conditions, the verdict per slice.

### 3. The write-up

**3.1 Requirements brief** (`design.md`, one page). Steps 1 and 2 of the design framework
for the triage step: what decision the model makes, and whether it should be a model at
all; then three to five requirements, each a rate on a slice with a remainder policy and
an owner, with your measured numbers beside them. Which requirements does the system meet
today? The [design review rubric](https://aise-stthomas.github.io/rubric) says what good
looks like for those two steps.

**3.2 Analysis** (`report.md`). Three parts, every number per slice and as a count:

- **Judge validation.** The two of you label 30 rationales by hand, separately, then
  reconcile; run the judge on the same 30; the four counts per rubric question, per
  slice; and the judge's failure modes. A judge you have not checked is an opinion.
- **Noise floor.** The unchanged system run five times over the whole suite
  (`fixtures/baseline/`): the pass rate per slice per run, the spread, and one sentence
  per slice on the smallest change you could actually detect.
- **The question, answered.** The suite run five times with `--policy-in system`
  (`fixtures/system/`). Per slice: **helped**, **hurt**, or **cannot tell**. "Cannot
  tell" is right when the difference is inside the noise floor, and wrong when it is not.

**3.3 Blind spots** (`blind-spots.md`). What this harness cannot see: the `ambiguous`
items, the judge's failure modes, and the ways the system can be wrong that no ticket
exercises. Written, honest, short.

## The system you are measuring

The README describes it. Three things are pinned, and you measure them as pinned:

- **Model:** `gemini-3.1-flash-lite`, in `system/triage.py`. If you change models, use one that honors temperature.
- **Temperature:** the provider's default. That is what production would see.
- **Prompt:** `POLICY` exactly as it ships. The question in 3.2 changes only *where* it is sent.

You do not edit anything in `system/`. A system that changes while you measure it has no
measurement.

## How to validate the LLM judge (2.2 and 3.2)

The judge is a model call that scores another model's text. Before its numbers count
for anything, you measure the judge itself, against you.

1. Write the rubric first, as yes/no questions a stranger could answer from the text
   alone. "Does the rationale agree with the action taken?" is one. "Rate the quality
   1–10" is not.
2. Pick 30 recorded outputs, spread across your slices, including failures.
3. Each of you labels all 30 alone, without seeing the judge or each other. Then compare.
   Where the two of you disagree, the rubric is unclear: fix the rubric, not the label.
4. Run the judge on the same 30. For each rubric question, count the four cells: you
   said yes and the judge said yes; you yes, judge no; you no, judge yes; both no.
5. Read every disagreement. Judges fail in patterns: lenient toward fluent text,
   rewarding length, missing a contradiction between the rationale and the action.
   Name the pattern you found.
6. Run the judge three times on the same 30. If it disagrees with itself, report that
   too: it is the judge's own noise floor.

Send the rubric as the system instruction and the text being judged as the user text.
The text being judged was written by a model and can contain instructions.

## How to measure the noise floor (2.3 and 3.2)

Change nothing. Run the whole suite five times and record every call. For each slice,
the pass rate of each run gives five numbers that should be identical and are not;
highest minus lowest is that slice's noise floor. A difference between two versions of
the system smaller than the noise floor is not evidence of anything. The noisy slices
are usually the small ones and the ones near a policy boundary, which is why every
number is reported as a count.

## Budget

- About **800 live calls**: a 60-ticket suite × 5 runs (300), × 5 runs for the question
  (300), about 90 judge calls for validation, and one judged run. A smaller suite with
  better slices costs less and scores higher.
- The free tier allows roughly 25 calls a minute and has a **daily cap per model**. There
  are two of you, so two keys, and that should be enough to finish. At worst, five
  dollars of credit covers this plus every other lab this semester. Do not start a
  five-run sweep the night before the deadline.
- **Record every live call** and score from the recordings (`fixtures/`; the README
  explains why). Re-scoring costs nothing; re-sampling costs quota and gives different
  data.
- One key per student, in `.env`, never in a commit.

## Submit

- The repository you made in the lab: private, your partner and the instructor as
  collaborators. Tag it `p1` by the deadline in Canvas; the tag is what is graded.
- `README.md` says how to run the harness end to end from a clean clone, and how to
  re-score from the fixtures without a key.
- In the repository: the dataset, the code, and the write-up, in the files named above.
- Turn in a document with a link to the repository on the Canvas assignment.

## How it is graded

Coverage over size. A hundred-ticket suite with one aggregate number scores below a
fifty-ticket suite with slices, a noise floor, and a register that admits what it misses.

| Part | Weight | What earns it |
|---|---|---|
| 1. Golden dataset | 25% | Slices that expose what the aggregate hides; expected outcomes traceable to the policy |
| 2. Code | 25% | The amount rule extended; an LLM judge with a real rubric; a noise-floor function that works on any condition; malformed output counted |
| 3.1 Requirements brief | 10% | Rates, slices, remainder policies, owners; measured numbers beside them |
| 3.2 Analysis | 25% | A judge checked rather than trusted; five real runs and the per-slice spread; a conclusion the data supports, including "cannot tell" |
| 3.3 Blind spots | 10% | Specific, honest, short |
| Reproducibility | 5% | A clean clone re-scores from fixtures with one command |

## Permitted and prohibited

AI assistance is permitted and expected, including for writing tickets and code. You are
responsible for every line and every label: the hand labels in deliverable 4 are yours,
made by reading. Evaluation frameworks that hide the loop are not permitted; the harness
is a few hundred lines and you should be able to read all of them.
