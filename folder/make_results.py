import os
import random
import matplotlib.pyplot as plt
from benchmark import make_case_chances, make_worse, DELTA
from fake_agent import run_cases_with_chances
from compare import case_changes, average, confidence_range, one_sided_range, decide

N_CASES = 100
N_RUNS = 5
N_EXPERIMENTS = 300

THRESHOLDS = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13]

def run_many(true_drop):
    observed_changes = []
    two_sided_verdicts = []
    one_sided_verdicts = []

    for i in range(N_EXPERIMENTS):
        old_chances = make_case_chances(N_CASES)
        new_chances = make_worse(old_chances, true_drop)
        old_version = run_cases_with_chances(old_chances, N_RUNS)
        new_version = run_cases_with_chances(new_chances, N_RUNS)
        changes = case_changes(old_version, new_version)
        observed_changes.append(average(changes))
        low, high = confidence_range(changes, n_rounds=500)
        two_sided_verdicts.append(decide(low, high, DELTA))
        low1, high1 = one_sided_range(changes, n_rounds=500)
        one_sided_verdicts.append(decide(low1, high1, DELTA))

    return observed_changes, two_sided_verdicts, one_sided_verdicts


def precent_regression(verdicts):
    count = 0
    for verdict in verdicts:
        if verdict == "REGRESSION":
            count = count + 1
    return 100*count / len(verdicts)


def percent_naive(observed_changes, threshold):
    count = 0
    for change in observed_changes:
        if change < -threshold:
            count = count + 1
    return 100 * count / len(observed_changes)


random.seed(42)
harmless_changes, harmless_two, harmless_one = run_many(0.03)
real_changes, real_two, real_one = run_many(0.08)


rows = []
rows.append(("Ours (two-sided 95%)", precent_regression(harmless_two), precent_regression(real_two)))
rows.append(("Ours (one-sided 95%)", precent_regression(harmless_one), precent_regression(real_one)))

for threshold in THRESHOLDS:
    name = "NAIVE, threshold " + str(threshold)
    rows.append((name, percent_naive(harmless_changes, threshold), percent_naive(real_changes, threshold)))


lines = []
lines.append("| Method | False alarms (harmless 0.03 drop) | Catches (real 0.08 drop) |")
lines.append("|---|---|---|")


for row in rows :
    lines.append("| "+row[0] + " | " + str(round(row[1], 1)) + "% | " + str(round(row[2], 1)) + "% |")
table_text = "\n".join(lines)
print(table_text)

os.makedirs("docs", exist_ok=True)
with open("docs/benchmark_table.md", "w") as f:
    f.write(table_text + "\n")

naive_x = []
naive_y = []

for row in rows[2: ]:
    naive_x.append(row[1])
    naive_y.append(row[2])

plt.figure(figsize=(7,6))
plt.plot(naive_x, naive_y, marker="o", color="gray", label="Naive (different thresholds)")
for i in range(len(THRESHOLDS)):
    plt.annotate(str(THRESHOLDS[i]), (naive_x[i], naive_y[i]),
                 textcoords="offset points", xytext=(5, 5), fontsize=8)
plt.scatter([rows[0][1]], [rows[0][2]], color="blue", s=100, label="Ours (two-sided)")
plt.scatter([rows[1][1]], [rows[1][2]], color="green", s=100, marker="s", label="Ours (one-sided)")
plt.xlabel("False alarms on harmless change (%)  - lower is better")
plt.ylabel("Real drops caught (%)  - higher is better")
plt.title("False alarms vs catches (100 cases x 5 runs)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("docs/benchmark_chart.png", dpi=150, bbox_inches="tight")
print("Saved docs/benchmark_table.md and docs/benchmark_chart.png")