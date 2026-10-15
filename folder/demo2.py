from fake_agent import run_all_cases, pass_rate

print("EXPERIMENT 1: Nothing changed (both versions pass 70% of the time)")
for attempt in range(10):
    old_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.7)
    new_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.7)
    change = pass_rate(new_version) - pass_rate(old_version)
    print("Attempt",attempt + 1, "- Change in pass rate: ", round(change, 3))

print()

print("EXPERIMENT 2: The new version is truly worse (60% instead of 70%)")
for attempt in range(10):
    old_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.7)
    new_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.6)
    change = pass_rate(new_version) - pass_rate(old_version)
    print("Attempt", attempt + 1, "- Change in pass rate: ", round(change, 3))