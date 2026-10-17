from benchmark import run_benchmark, DELTA

print("delta =", DELTA, "-> a drop of more than 5 points is a real problem")
print()
print("true drop | ours: REGRESSION | ours: OK | ours: INCONCLUSIVE | naive: REGRESSION")

for true_drop in [0.00, 0.03, 0.08, 0.12]:
    r = run_benchmark(true_drop, n_experiments=500)
    print(
        " ", true_drop, "     |",
        round(r["ours_regression"] * 100), "%        |",
        round(r["ours_ok"] * 100), "%     |",
        round(r["ours_inconclusive"] * 100), "%            |",
        round(r["naive_regression"] * 100), "%",
    )