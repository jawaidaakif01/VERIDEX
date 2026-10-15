from fake_agent import run_all_cases
from compare import case_changes, average, confidence_range, decide, estimate_cases_needed

delta = 0.05
n_cases = 20

old_version = run_all_cases(n_cases=n_cases, n_runs=5, pass_chance=0.7)
new_version = run_all_cases(n_cases=n_cases, n_runs=5, pass_chance=0.6)

changes = case_changes(old_version, new_version)
observed = average(changes)

low, high = confidence_range(changes)
verdict = decide(low, high, delta)

print("Change: ", round(observed, 3), "| range:", round(low, 3), "to", round(high, 3))
print("Verdict: ", verdict)

needed = estimate_cases_needed(observed, low, high, delta, n_cases)
if needed is None:
    print("The verdict is already clear. No extra cases needed.")
elif needed > 5000:
    print("More than 5000 test cases would be needed.")
    print("The change is too close to your delta line to settle cheaply.")
else:
    print("Rough estimate: about", needed, "test cases needed (you have" , n_cases, ")")
