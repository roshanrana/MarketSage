import pytest

from marketsage_eval.scenarios import SCENARIOS, run_scenario


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.name for s in SCENARIOS])
def test_fault_is_handled_honestly(scenario, tmp_path):
    outcome = run_scenario(scenario, tmp_path)

    assert outcome.passed, f"{scenario.name}: expected {scenario.expected}, {outcome.detail}"


def test_every_scenario_has_a_distinct_name():
    names = [scenario.name for scenario in SCENARIOS]

    assert len(names) == len(set(names))
