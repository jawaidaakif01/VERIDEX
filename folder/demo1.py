from fake_agent import run_all_cases, pass_rate

# Version A for our agent: 5 test cases, each run 4 times
version_a = run_all_cases(n_cases=5, n_runs=4, pass_chance=0.7)
print("Version A results: ", version_a)
print("Version A pass rate: ", pass_rate(version_a))

print()

# Version B is the same agent. Nothing changed. Let's run it again
version_b = run_all_cases(n_cases=5, n_runs=4, pass_chance=0.7)
print("Version B results: ", version_b)
print("Version B pass rate: ", pass_rate(version_b))