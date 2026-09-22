# P1 — Measure it

The evaluation harness is the single most important artifact in this course. It is the
AI system's test suite, its specification, and its release gate at once. P1 is where you
build your first one, and everything you ship later is gated on it.

You do not need to know anything about agents for this project. The system you are
measuring is one model call that makes one consequential decision.

## The system you are measuring

The system under test is the triage step you met in the *feel the distribution* lab: the `triage()` function, frozen in this project's repository,
[measure-it](https://github.com/aise-stthomas/measure-it). It renders a ticket and an account summary into a prompt, takes one sample from the model, and parses the result into `{action, refund_amount, rationale}`. The policy it is
supposed to follow is the `POLICY` text in `triage.py`. That is the component.
Everything you measure is about that component.

- **Model:** `gemini-3.1-flash-lite`. If you change models, make sure the new one honors temperature.
- **Temperature:** the provider's default. That is what production would see.
- **Prompt:** `POLICY` exactly as it ships (`policy_in="user"`).

## Where you start

In the repository you made in the lab, from the [measure-it](https://github.com/aise-stthomas/measure-it)
template. It holds the frozen system under test (`triage.py`), the golden-set format
with your first tickets, a recorder that keeps every live call (`record.py`), and a
scoring skeleton with three scorers written (`score.py`). Everything marked `YOURS` is
the project. You do not edit `triage.py`.

The full Operator scaffold arrives with a later project, and your harness will port to it
without changes, because its output has the same shape.

## Deliver

1. **A golden set** of 50–80 tickets, each with the outcome the policy requires. You write them: realistic tickets across the intents the policy covers, plus
   hand-authored edge and adversarial items. Each item records the ticket, the account,
   the expected action, the most the refund may be (if any), its slice tags, and one
   line saying which sentence of the policy makes that the right answer. If the two of
   you cannot agree on the right answer for a ticket, do not force it: tag it
   `ambiguous` and keep it.
2. **Slices.** At minimum: by intent; by refund amount relative to the caps (well
   under, near, over $50, over $200); by whether the ticket contains text addressed to
   the model; and one slice of your own choosing that you expect to fail. Every number
   you report is per slice, with the count beside it. "4 of 6" is a finding. "67%" on
   six items is a decoration.
3. **Scorers** for each part of the output: exact match for the action; a rule for the
   amount (within the cap, and not a number that appears nowhere in the ticket or the
   account); malformed output counted as a failure, never dropped. For the rationale
   text, a **model judge** with a written rubric. At minimum the rubric asks: does the
   rationale agree with the action that was actually taken, and does it state the
   policy correctly? You have already seen both fail.
4. **A validated judge.** Before you look at any judge output, the two of you label 30
   rationales by hand, separately, then reconcile. Then run the judge on the same 30.
   Report where the judge and your labels agree and disagree, as counts, per slice,
   and describe the judge's failure modes you found. A judge you have not checked is
   an opinion.
5. **The noise floor.** Run the unchanged system over the whole suite five times.
   Report the pass rate per slice for each run and the spread across runs. Then say, in
   one sentence per slice, the smallest change you could actually detect.
6. **One question, answered with your harness.** There is a second way to send the
   prompt: `--policy-in system` puts the policy in the system instruction instead of
   beside the ticket (see `render()` in `triage.py`). Run the suite five
   times that way. **Per slice: did it help, did it hurt, or can you not tell?** "Cannot
   tell" is an acceptable answer when the difference is inside your noise floor, and a
   wrong answer when it is not.
7. **The blind-spot register.** What this harness cannot see. Written, honest, short.
   The `ambiguous` items, the judge's failure modes, and the ways this system can be
   wrong that no ticket exercises all belong here.
8. **A one-page requirements brief** (`design.md`): steps 1 and 2 of the seven-step
   framework for the triage step. What decision does the model
   make, and should it be a model at all? Then three to five requirements, each written
   as a rate, on a slice, with a remainder policy and an owner. Your measured numbers go
   beside them: which requirements does the system meet today? The
   [design review rubric](https://aise-stthomas.github.io/rubric) describes what good
   looks like for those two steps.

## How to do the two parts we have not covered yet

Evaluation gets its own weeks later in the course, after this is due. That is deliberate: you
will get more from them having built one. Until then, these two recipes are
enough.

**Validating a judge.**

1. Write the rubric first, as yes/no questions a stranger could answer from the text.
2. Pick 30 outputs from a recorded run, spread across your slices, including failures.
3. Each of you labels all 30 alone, without seeing the judge or each other. Compare.
   Where the two of you disagree, the rubric is unclear: fix the rubric, not the label.
4. Run the judge on the same 30. Build the two-by-two table for each rubric question:
   you said yes or no, the judge said yes or no. Report the four counts.
5. Read every disagreement. Most judges fail in a pattern: they are lenient toward
   fluent text, they reward length, they miss a contradiction between the rationale
   and the action. Name the pattern you found.
6. Run the judge three times on the same 30. If it disagrees with itself, that is a
   noise floor too. Report it.

The judge is a model call. Everything you know about what a model receives applies to it: the rubric
belongs in the system instruction, the text being judged belongs in the user text, and
the text being judged was written by a model and can contain instructions.

**Measuring a noise floor.**

1. Change nothing. Run the whole suite five times and record every call.
2. For each slice, compute the pass rate of each run. You now have five numbers per
   slice that *should* be identical and are not.
3. The spread, highest minus lowest, is your noise floor for that slice. A difference
   between two versions of the system that is smaller than the spread is not evidence
   of anything.
4. Notice which slices are noisy. It is usually the small ones and the ones near a
   policy boundary. Small slices are why deliverable 2 asks for counts.

Later in the course, "highest minus lowest" is replaced with something better. It will not change the
habit: no comparison without a noise floor.

## Budget

- About **800 live calls**: a 60-ticket suite × 5 runs for the noise floor (300), × 5
  runs for deliverable 6 (300), about 90 judge calls for validation, and one judged
  run. A smaller suite with better slices costs less and scores higher.
- The free tier allows roughly 25 calls a minute, and it also has a **daily cap per
  model**. There are two of you, so you have two keys, and that should be enough to finish. At worst, five dollars of credit will cover this plus every other lab this semester. Do not start a five-run sweep the night before the deadline.
- **Record every live call** and score from the recordings. The repository calls a saved
  model output a *fixture* and keeps them under `fixtures/`; its README explains why.
  Re-scoring costs nothing; re-sampling costs quota, and gives you different data.
- One key per student, in `.env`, never in a commit.

## Submit

- One GitHub repository per pair, private, with the instructor added as a
  collaborator. Tag it `p1` by the deadline in Canvas; the tag is what is graded.
- `README.md` says how to run the harness end to end from a clean clone, and how to
  re-score from the fixtures without a key.
- In the repository: the golden set, the fixtures, the per-slice report, the judge
  rubric and its validation, the noise-floor numbers, the answer to deliverable 6, the
  blind-spot register, and design.
- Turn in a document with a link to the GitHub repository on the Canvas assignment.

## How it is graded

Coverage over size. A hundred-ticket suite with one aggregate number scores below a
fifty-ticket suite with slices, a noise floor, and a register that admits what it
misses.

| Part | Weight | What earns it |
|---|---|---|
| Golden set and slices (1, 2) | 25% | Slices that expose what the aggregate hides; expected outcomes traceable to the policy; coverage mapped to your hazards |
| Scorers and judge validation (3, 4) | 25% | A judge you checked rather than trusted; its failure modes named; malformed output counted |
| Noise floor and the answered question (5, 6) | 25% | Five real runs; per-slice spread; a conclusion the data supports, including "cannot tell" |
| Blind-spot register (7) | 10% | Specific, honest, short |
| Requirements brief (8) | 10% | Rates, slices, remainder policies, owners; measured numbers beside them |
| Reproducibility | 5% | A clean clone re-scores from fixtures with one command |

## Permitted and prohibited

AI assistance is permitted and expected, including for writing tickets and code. You
are responsible for every line and every label: the hand labels in deliverable 4 are
yours, made by reading. Evaluation frameworks that hide the loop are not permitted; the
harness is a few hundred lines and you should be able to read all of them.
