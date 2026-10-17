import random
from fake_agent import run_cases_with_chances
from compare import case_changes, average, confidence_range, decide

DELTA = 0.05

def make_case_chances(n_cases):
    '''Give every test case its own pass chance, somewhere between 0.2 and 1.0'''
    chances = []
    for i in range(n_cases):
        chances.append(random.uniform(0.2, 1.0))
    return chances


def make_worse(chances, drop):
    '''Make every case a bit worse by lowering its pass chance.'''
    
    worse = []
    for chance in chances:
        new_chance = chance - drop
        if new_chance < 0:
            new_chance = 0
        worse.append(new_chance)
    return worse

def run_one_experiment(true_drop, n_cases=50, n_runs = 5):
    '''Simulate ONE experiment. Returns (our verdict, naive vedict).'''
    old_chances = make_case_chances(n_cases)
    new_chances = make_worse(old_chances, true_drop)

    old_version = run_cases_with_chances(old_chances, n_runs)
    new_version = run_cases_with_chances(new_chances, n_runs)

    changes = case_changes(old_version, new_version)
    observed = average(changes)

    low, high = confidence_range(changes, n_rounds=500)
    our_verdict = decide(low, high, DELTA)

    if observed < -DELTA:
        naive_verdict = "REGRESSION"
    else:
        naive_verdict = "OK"

    return our_verdict, naive_verdict

def run_benchmark(true_drop, n_experiments=500, n_cases=50, n_runs=5):
    '''Repeat the experiment many times and count what each method says.'''
    our_regression = 0
    our_ok = 0
    our_inconclusive = 0
    naive_regression = 0

    for i in range(n_experiments):
        our_verdict, naive_verdict = run_one_experiment(true_drop, n_cases, n_runs)

        if our_verdict == "REGRESSION":
            our_regression = our_regression + 1
        elif our_verdict == "NO_MATERIAL_REGRESSION":
            our_ok = our_ok + 1
        else:
            our_inconclusive = our_inconclusive + 1

        if naive_verdict == "REGRESSION":
            naive_regression = naive_regression + 1

    return {
        "ours_regression": our_regression / n_experiments,
        "ours_ok": our_ok / n_experiments,
        "ours_inconclusive": our_inconclusive / n_experiments,
        "naive_regression": naive_regression / n_experiments,
    }