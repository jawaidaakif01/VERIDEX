from fake_agent import run_all_cases
from compare import case_changes, average, confidence_range, decide

delta = 0.05

for n_cases in [20, 100, 400]:
    old_version = run_all_cases(n_cases=n_cases, n_runs=5, pass_chance=0.7)
    new_version = run_all_cases(n_cases=n_cases, n_runs=5, pass_chance=0.6)

    changes = case_changes(old_version, new_version)
    low, high = confidence_range(changes)
    verdict = decide(low, high, delta)

    print(n_cases, "cases | change:", round(average(changes), 3),
          
          "| range:", round(low, 3), "to", round(high, 3), "|", verdict)

    