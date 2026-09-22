"""YOURS (deliverables 3 and 4). The judge for the rationale text.

Nothing is written here on purpose. What the spec asks for, in the order that works:

1. The rubric, as yes/no questions a stranger could answer from the text alone.
2. Thirty rationales from a recorded run, labelled by each of you alone, then
   reconciled. Keep the labels in a file in this repository.
3. The judge: one model call per rationale. The rubric goes in the system instruction,
   the text being judged goes in the user text, and the text being judged was written
   by a model, so it can contain instructions. Record every judge call as a fixture.
4. The two-by-two table, judge against your labels, per rubric question, as counts.
5. The same thirty, judged three times. Does the judge agree with itself?

system/triage.py shows how to make a model call and parse what comes back. Write a new
call here rather than changing that file: it is the system under test.
"""
