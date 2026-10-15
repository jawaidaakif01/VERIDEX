from fake_agent import run_all_cases
from compare import case_changes, average, confidence_range

old_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.7)
new_version = run_all_cases(n_cases=20, n_runs=5, pass_chance=0.6)

changes = case_changes(old_version, new_version)
observed = average(changes)
low, high = confidence_range(changes)

print("Average change: ", round(observed, 3))
print("95% range: from", round(low, 3), "to", round(high, 3))

if high < 0:
    print("The whole range is below zero: the new version looks worse.")
elif low > 0:
    print("The whole range is above zero, the new version looks better.")
else:
    print("The range includes zero: we can't be sure anything changed.")

