from benchmark import make_case_chances, make_worse, DELTA
from fake_agent import run_cases_with_chances
from compare import case_changes, confidence_range, one_sided_range, decide


def run_many(true_drop, n_experiments, n_cases, n_runs):
    two_sided = []
    one_sided = []

    for i in range(n_experiments):
        old_chances = make_case_chances(n_cases)
        new_chances = make_worse(old_chances, true_drop)
        old_version = run_cases_with_chances(old_chances, n_runs)
        new_version = run_cases_with_chances(new_chances, n_runs)
        changes = case_changes(old_version, new_version)

        low, high = confidence_range(changes, n_rounds=500)
        two_sided.append(decide(low, high, DELTA))

        low1, high1 = one_sided_range(changes, n_rounds=500)
        one_sided.append(decide(low1, high1, DELTA))
    return two_sided, one_sided


def percent_regression(verdicts):
    count = 0
    for verdict in verdicts:
        if verdict == "REGRESSION":
            count = count + 1

    return 100 * count / len(verdicts)

