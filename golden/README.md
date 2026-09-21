# The golden set

`golden.jsonl` is one ticket per line. Three examples are here so you can see the format
and run the harness on day one. Replace or keep them; you need 50–80.

| Field | Meaning |
|---|---|
| `id` | Yours. Unique. It is how a recorded call finds its ticket again. |
| `account` | A name from `accounts.json`. Add accounts as your tickets need them. The model sees the whole account summary, so the account is part of the test. |
| `ticket` | What the customer wrote. |
| `expected_action` | `answer`, `refund`, `hold`, or `escalate`: what the policy in `triage.py` requires. |
| `max_refund` | The most a correct output may propose, or `null` if no amount belongs in the output. |
| `slices` | Tags, `name:value`. Every tag becomes a row in your report. Decide your slice names once and spell them the same way every time. |
| `policy` | The sentence of the policy that makes `expected_action` right. If you cannot quote one, that is a finding. |
| `ambiguous` | `true` when the two of you could not agree. Keep the item. It belongs in your blind-spot register. |
