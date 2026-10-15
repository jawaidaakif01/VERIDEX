from fake_agent import run_all_cases
from compare import case_changes, average, one_bootstrap_round

old_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.7)
new_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.6)

changes = case_changes(old_version, new_version)
print("Change for each test case: ", changes)
print("Average change: ", round(average(changes), 3))

print()
print("Now let's wobble it: 5 bootstrap rounds")
for round_number in range(5):
    wobble = one_bootstrap_round(changes)
    print("Round", round_number + 1, "- average change: ", round(wobble, 3))

print(changes)