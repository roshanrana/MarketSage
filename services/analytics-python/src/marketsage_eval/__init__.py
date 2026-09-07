"""Offline evaluation harness.

Everything here runs in-process against the committed fixtures with the
deterministic providers bound: no network, no API key, no model download and
no random number generator. ``python -m marketsage_eval`` writes
``metrics/headline.json`` (the numbers the README card shows) and
``metrics/eval-latest.json`` (the full detail, including timings that are not
stable enough to commit).
"""
