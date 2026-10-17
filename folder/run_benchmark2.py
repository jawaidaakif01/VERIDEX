from benchmark import run_benchmark

print("Does a bigger experiment help? (5 runs per case, 200 experiments each)")
print()
print("Cases | drop 0.03 (harmless): ours / naive flag it | drop 0.08 (real): ours catches / naive catches / our INCONCLUSIVE")

for n_cases in [50, 100, 200, 400]:
    small = run_benchmark(0.03, n_experiments=200, n_cases=n_cases, n_runs=5)
    real = run_benchmark(0.08, n_experiments=200, n_cases=n_cases, n_runs=5)
    print(
        n_cases, " |",
        round(small["ours_regression"] * 100), "% /",
        round(small["naive_regression"] * 100), "% |",
        round(real["ours_regression"] * 100), "% /",
        round(real["naive_regression"] * 100), "% /",
        round(real["ours_inconclusive"] * 100), "%",
    )