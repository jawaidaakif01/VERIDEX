import random
import pytest

from fake_agent import run_all_cases, pass_rate
from compare import case_pass_rate, case_changes, average, confidence_range, decide, find_flaky_cases, count_case_types, estimate_cases_needed




def test_average():
    assert average([1,2,3]) == 2

def test_case_pass_rates():
    results = [[1,1,0,0], [1,1,1,1]]
    assert case_pass_rate(results) == [0.5, 1.0]

def test_case_changes():
    old = [[1,1,0,0], [1,1,1,1]]
    new = [[1,0,0,0], [1,1,1,1]]
    assert case_changes(old, new) == [-0.25, 0.0]



def test_fake_agent_has_the_right_shape():
    results = run_all_cases(n_cases=7, n_runs=3, pass_chance=0.5)
    assert len(results) == 7
    assert len(results[0]) == 3

def test_agent_that_always_passes():
    results = run_all_cases(n_cases=5, n_runs=5, pass_chance=1.0)
    assert pass_rate(results) == 1.0

def test_agent_that_never_passes():
    results = run_all_cases(n_cases=5, n_runs=5, pass_chance=0.0)
    assert pass_rate(results) == 0.0



def test_decide_regression():
    assert decide(-0.20, -0.10, delta=0.05) == "REGRESSION"


def test_decide_no_material_regression():
    assert decide(-0.02, 0.04, delta=0.05) == "NO_MATERIAL_REGRESSION"


def test_decide_inconclusive():
    assert decide(-0.10, 0.02, delta=0.05) == "INCONCLUSIVE"



def test_range_contains_the_average():
    random.seed(1)
    changes = [-0.2, 0.0, -0.4, 0.2, -0.2, -0.6, 0.0, 0.2, -0.2, -0.4]
    low, high = confidence_range(changes)
    assert low <= average(changes) <= high

def test_same_numbers_give_tiny_range():
    changes = [-0.1] * 10
    low, high = confidence_range(changes)

    assert low == pytest.approx(-0.1)
    assert high == pytest.approx(-0.1)

def test_more_cases_give_a_narrower_range():
    random.seed(2)
    few_cases = [-0.2, 0.2] * 10
    many_cases = [-0.2, 0.2] * 100
    low_few, high_few = confidence_range(few_cases)
    low_many, high_many = confidence_range(many_cases)

    assert (high_many - low_many) < (high_few - low_few)



def test_nothing_changed_means_no_material_regression():
    old = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.7)
    changes = case_changes(old, old)
    low, high = confidence_range(changes)

    assert decide(low, high, delta = 0.05) == "NO_MATERIAL_REGRESSION"

def test_a_big_drop_is_a_regression():
    random.seed(5)
    old = run_all_cases(n_cases=200, n_runs=5, pass_chance=0.9)
    new = run_all_cases(n_cases=200, n_runs=5, pass_chance=0.5)

    changes = case_changes(old, new)

    low, high = confidence_range(changes)

    assert decide(low, high, delta=0.05) == "REGRESSION"


def test_find_flaky_cases():
    results = [[1,1,1,1], [0,0,0,0], [1,0,1,1]]
    assert find_flaky_cases(results) == [(3, 0.75)]

def test_count_case_types():
    results = [[1,1], [1,1], [0,0], [1,0]]
    assert count_case_types(results) == (2,1,1)



def test_no_estimate_when_verdict_is_clear():
    assert estimate_cases_needed(-0.15, -0.20, -0.10, 0.05, 50) is None

def test_estimate_when_inconclusive():
    needed = estimate_cases_needed(-0.10, -0.20, 0.00, 0.05, 50)
    assert needed > 50