from fake_agent import run_cases_with_chances
from compare import find_flaky_cases, count_case_types

chances = [1.0, 1.0, 0.95, 0.9, 0.7, 0.5, 0.3, 0.1, 0.0, 0.0]
results = run_cases_with_chances(chances, n_runs=10)

for i in range(len(results)):
    print("Case", i+1, "(true chance", chances[i], "):", results[i])

print()
print("Flaky cases:")
for case_number, rate in find_flaky_cases(results):
    print(" Case", case_number, "passed", round(rate * 100), "% of its runs")

print()

always_pass, always_fail, flaky = count_case_types(results)
print("Always pass: ", always_pass)
print("Always fail: ", always_fail)
print("Flaky:", flaky)

