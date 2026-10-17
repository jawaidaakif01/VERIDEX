from fair2 import run_many, percent_regression

harmless_two, harmless_one = run_many(0.03, 300, 100, 5)
real_two, real_one = run_many(0.08, 300, 100, 5)

print("100 cases x 5 runs, 300 experiments per scenario")
print("two_sided 95% | false alarms:", round(percent_regression(harmless_two)),
      "% | catches:", round(percent_regression(real_two)), "%")
print("one-sided 95% | false alarms:", round(percent_regression(harmless_one)),
      "% | catches:", round(percent_regression(real_one)), "%") 

