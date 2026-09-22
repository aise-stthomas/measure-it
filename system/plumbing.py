"""Plumbing: retrying when the provider says "slow down", and a fake provider for
checking your harness with no key. Not part of the system under test.
"""
from __future__ import annotations

import json
import random
import time


def with_retries(sample):
    """Wrap a sample(prompt, temperature, model) function so a run finishes.

    The free tier *is* a per-minute rate limit: a 429 means "the minute is not over
    yet", so sleep briefly and try again. A daily cap, a billing problem, or a provider
    that keeps returning 5xx will not get better by waiting, so stop and say why.
    """
    def call(prompt: str, temperature: float | None, model: str, system: str | None = None) -> str:
        from google.genai import errors

        switch = ("Everything recorded so far is kept: rerun the same command later (or "
                  "with your partner's key) and it continues where it stopped.")
        delay, server_errors = 5, 0
        for _ in range(30):
            try:
                return sample(prompt, temperature, model, system)
            except errors.ClientError as e:
                if e.code != 429:
                    raise
                msg = getattr(e, "message", str(e))
                if any(w in msg.lower() for w in ("day", "depleted", "billing", "credits")):
                    raise SystemExit(f"\n{model} refused: {msg[:200]}\n{switch}")
                print(f"    rate limited; sleeping {delay}s", flush=True)
                time.sleep(delay)
            except errors.ServerError as e:
                server_errors += 1
                if server_errors == 1:
                    print(f"    server error {e.code}: {getattr(e, 'message', str(e))[:120]}", flush=True)
                if server_errors >= 5:
                    raise SystemExit(f"\n{model} keeps returning {e.code}; that is the provider, not you. {switch}")
                print(f"    retrying in {delay}s", flush=True)
                time.sleep(delay)
        raise SystemExit(f"\nGave up after repeated rate limits on {model}. {switch}")
    return call


def fake_model(prompt: str, temperature: float | None, model: str, system: str | None = None) -> str:
    """NOT a model. Returns a random decision so you can check your harness (recording,
    scoring, tables) with no key and no quota. Any conclusion you draw from fake output
    is a conclusion about this function, not about a model.
    """
    import re
    dollars = [float(x) for x in re.findall(r"\$(\d+(?:\.\d+)?)", prompt.split("TICKET:")[-1])]
    action = random.choices(["answer", "refund", "hold", "escalate"], weights=[4, 3, 2, 1])[0]
    amount = random.choice(dollars) if dollars and action in ("refund", "hold") else None
    if random.random() < 0.03:
        return "Sure! Here is my decision: refund it."  # malformed on purpose
    return json.dumps({"action": action, "refund_amount": amount, "rationale": "fake"})
