from benchmark import make_case_chances, make_worse, DELTA
from fake_agent import run_cases_with_chances
from compare import case_changes, average, confidence_range, decide


def run_many(true_drop, n_experiments, n_cases, n_runs):
    observed_changes = []
    our_verdicts = []

    for i in range(n_experiments):
        old_chances = make_case_chances(n_cases)
        new_chances = make_worse(old_chances, true_drop)
        old_version = run_cases_with_chances(old_chances, n_runs)
        new_version = run_cases_with_chances(new_chances, n_runs)
        changes = case_changes(old_version, new_version)
        observed_changes.append(average(changes))
        low, high = confidence_range(changes, n_rounds=500)
        our_verdicts.append(decide(low, high, DELTA))
    return observed_changes, our_verdicts

def percent_flagged_by_ours(our_verdicts):
    count = 0
    for verdict in our_verdicts:
        if verdict == "REGRESSION":
            count = count + 1
    return 100 * count / len(our_verdicts)


def percent_flagged_by_naive(observed_changes, threshold):
    count = 0
    for change in observed_changes:
        if change < -threshold:
            count = count + 1

    return 100 * count / len(observed_changes)

