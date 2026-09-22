# P1 — Measure it

**The ask.** Build an evaluation harness for the triage system in this repository, and
use it to answer one question with evidence: does sending the policy as the system
instruction, instead of beside the ticket, help? Your answer is per slice, with a noise
floor, with a judge you validated, and with an honest list of what the harness cannot
see.

The harness is the AI system's test suite, its specification, and its release gate at
once. Everything you ship later in the course is gated on one. You do not need to know
anything about agents for this project: the system under test is one model call that
makes one consequential decision.

## Deliverables

| # | Deliverable | Where it lives | The bar |
|---|---|---|---|
| 1 | **Golden set**: 50–80 tickets, each with the action the policy requires, the most the refund may be, slice tags, and the policy sentence that makes the answer right. Tickets the two of you cannot agree on stay in, tagged `ambiguous`. | `golden/golden.jsonl` | Realistic tickets across every intent the policy covers, plus edge and adversarial items you wrote by hand. |
| 2 | **Slices**: at minimum by intent; by amount relative to the caps (well under, near, over \$50, over \$200); by whether the ticket contains text addressed to the model; and one of your own that you expect to fail. | slice tags on every ticket | Every number you report is per slice, as a count. "4 of 6" is a finding; "67%" on six items is a decoration. |
| 3 | **Scorers**: exact match for the action; a rule for the amount (within the cap, and not a number that appears nowhere in the ticket or account); malformed output counted as a failure; a **model judge** with a written rubric for the rationale. | `harness/scorers.py`, `harness/judge.py` | The rubric asks at least: does the rationale agree with the action taken, and does it state the policy and the arithmetic correctly? Both fail in this system's output: one rationale ends "choosing to hold since it exceeds my limit" on a `refund` of \$52.99; another says the total "is under \$50" when it is \$52.99. |
| 4 | **A validated judge**: the two of you label 30 rationales by hand, separately, then reconcile; run the judge on the same 30; report agreement and disagreement as counts, per slice, and the judge's failure modes. | `judge-validation.md` and the labels file | A judge you have not checked is an opinion. |
| 5 | **The noise floor**: the unchanged system run five times over the whole suite; the pass rate per slice per run, and the spread. | `fixtures/baseline/`, `report.md` | One sentence per slice: the smallest change you could actually detect. |
| 6 | **The question, answered**: the suite run five times with `--policy-in system`; per slice, **helped**, **hurt**, or **cannot tell**. | `fixtures/system/`, `report.md` | "Cannot tell" is right when the difference is inside the noise floor, and wrong when it is not. |
| 7 | **Blind-spot register**: what this harness cannot see. | `blind-spots.md` | Written, honest, short. The `ambiguous` items, the judge's failure modes, and the ways the system can be wrong that no ticket exercises. |
| 8 | **Requirements brief**: steps 1 and 2 of the design framework for the triage step. What decision does the model make, and should it be a model at all? Then three to five requirements, each a rate on a slice with a remainder policy and an owner, with your measured numbers beside them. | `design.md`, one page | Which requirements does the system meet today? The [design review rubric](https://aise-stthomas.github.io/rubric) says what good looks like for those two steps. |

## The system you are measuring

The README describes it. Three things are pinned, and you measure them as pinned:

- **Model:** `gemini-3.1-flash-lite`, in `system/triage.py`. If you change models, use one that honors temperature.
- **Temperature:** the provider's default. That is what production would see.
- **Prompt:** `POLICY` exactly as it ships. Deliverable 6 changes only *where* it is sent.

You do not edit anything in `system/`. A system that changes while you measure it has no
measurement.

## Two recipes

Evaluation gets its own lectures later; these are enough to do deliverables 4 and 5 now.

**Validating a judge.**

1. Write the rubric first, as yes/no questions a stranger could answer from the text.
2. Pick 30 outputs from a recorded run, spread across slices, including failures.
3. Each of you labels all 30 alone, without seeing the judge or each other. Compare.
   Where you disagree, the rubric is unclear: fix the rubric, not the label.
4. Run the judge on the same 30. For each rubric question, the two-by-two table: you
   said yes or no, the judge said yes or no. Report the four counts.
5. Read every disagreement. Judges fail in patterns: lenient toward fluent text, rewarding
   length, missing a contradiction between the rationale and the action. Name yours.
6. Run the judge three times on the same 30. If it disagrees with itself, that is a noise
   floor too. Report it.

The judge is a model call: the rubric goes in the system instruction, the text being
judged goes in the user text, and the text being judged was written by a model and can
contain instructions.

**Measuring a noise floor.**

1. Change nothing. Run the whole suite five times; record every call.
2. For each slice, the pass rate of each run: five numbers that should be identical and
   are not.
3. Highest minus lowest is the noise floor for that slice. A difference between two
   versions smaller than it is not evidence of anything.
4. The noisy slices are usually the small ones and the ones near a policy boundary.
   That is why deliverable 2 asks for counts.

## Budget

- About **800 live calls**: a 60-ticket suite × 5 runs (300), × 5 runs for deliverable 6
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
- In the repository: everything in the deliverables table, in the files it names.
- Turn in a document with a link to the repository on the Canvas assignment.

## How it is graded

Coverage over size. A hundred-ticket suite with one aggregate number scores below a
fifty-ticket suite with slices, a noise floor, and a register that admits what it misses.

| Part | Weight | What earns it |
|---|---|---|
| Golden set and slices (1, 2) | 25% | Slices that expose what the aggregate hides; expected outcomes traceable to the policy |
| Scorers and judge validation (3, 4) | 25% | A judge you checked rather than trusted; its failure modes named; malformed output counted |
| Noise floor and the answered question (5, 6) | 25% | Five real runs; per-slice spread; a conclusion the data supports, including "cannot tell" |
| Blind-spot register (7) | 10% | Specific, honest, short |
| Requirements brief (8) | 10% | Rates, slices, remainder policies, owners; measured numbers beside them |
| Reproducibility | 5% | A clean clone re-scores from fixtures with one command |

## Permitted and prohibited

AI assistance is permitted and expected, including for writing tickets and code. You are
responsible for every line and every label: the hand labels in deliverable 4 are yours,
made by reading. Evaluation frameworks that hide the loop are not permitted; the harness
is a few hundred lines and you should be able to read all of them.
