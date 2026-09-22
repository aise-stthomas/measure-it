"""Scorers: each turns (item, output) into True, False, or None (does not apply).

SCORERS names them. Adding a check is adding a row. Everything marked YOURS is the project.
"""
from __future__ import annotations


def score_action(item: dict, output: dict) -> bool:
    """Exact match on the route. Malformed output is a failure, never dropped."""
    return output["action"] == item["expected_action"]


def score_amount(item: dict, output: dict) -> bool | None:
    """The proposed amount never exceeds the most the policy allows for this ticket.

    YOURS to extend (deliverable 2.1): also not above what the action itself permits, and
    not a number that appears nowhere in the ticket or the account.
    """
    if item["max_refund"] is None:
        return output["refund_amount"] is None
    if output["refund_amount"] is None:
        return None  # nothing proposed; the action scorer decides
    return output["refund_amount"] <= item["max_refund"]


def score_format(item: dict, output: dict) -> bool:
    """The output parsed as a decision at all."""
    return output["action"] != "malformed"


def score_rationale(item: dict, output: dict) -> bool | None:
    """The LLM judge's verdict (harness/judge.py), recorded by judge.py.

    Passes when the judge answered yes to every rubric question. None until the judge has
    been run on this output. YOURS (deliverable 2.2): extend the rubric, then validate it.
    """
    verdicts = output.get("judge")
    if verdicts is None:
        return None
    return all(verdicts.values())


SCORERS = {  # name: (function, what it checks)
    "action":    (score_action,    "the route is the one the policy requires"),
    "amount":    (score_amount,    "the amount never exceeds what the policy allows"),
    "format":    (score_format,    "the output parsed as a decision"),
    "rationale": (score_rationale, "the LLM judge says the reason holds up"),
}
