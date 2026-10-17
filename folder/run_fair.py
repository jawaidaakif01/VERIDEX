from fair_benchmark import run_many, percent_flagged_by_naive, percent_flagged_by_ours

n_cases = 100
n_runs = 5
thresholds = [0.05, 0.07, 0.09, 0.11, 0.13]

harmless_changes, harmless_ours = run_many(0.03, 300, n_cases, n_runs)
real_changes, real_ours = run_many(0.08, 300, n_cases, n_runs)

print("100 cases x 5 runs, 300 experiments scenario")
print("false alarms = flagged a harmless 0.03 drop | catches = flagged a real 0.08 drop")
print()
print("OURS (range method)   | false alarms:",
        round(percent_flagged_by_ours(harmless_ours)), "% | catches:",
        round(percent_flagged_by_ours(real_ours)), "%"
      )

print()

for threshold in thresholds:
    print("naive, threshold", threshold, "| false alarms:",
          round(percent_flagged_by_naive(harmless_changes, threshold)), "% | catches:",
          round(percent_flagged_by_naive(real_changes, threshold)), "%")

    
    