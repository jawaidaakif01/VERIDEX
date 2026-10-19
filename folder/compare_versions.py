import os
from triage_cases import cases
from storage import load_records
from bridge import records_to_results
from compare import (case_changes, average, confidence_range, one_sided_range,
                     decide, estimate_cases_needed)

DELTA = 0.05
BASELINE_NAME = "v0_baseline"
OTHER_NAMES = ["v1_aa_rerun", "v2_reworded", "v3_placeholder_bug", "v4_strict_priority"]


def file_for(name):
    return "results/triage_" + name + ".jsonl"


def count_errors(records):
    count = 0
    for record in records:
        if record.error is not None:
            count = count + 1
    return count


def overall_pass_rate(records):
    passed = 0
    for record in records:
        if record.passed:
            passed = passed + 1
    return passed / len(records)


def compare_two(old_records, new_records):
    old_results = records_to_results(old_records, cases)
    new_results = records_to_results(new_records, cases)
    changes = case_changes(old_results, new_results)
    observed = average(changes)

    low, high = confidence_range(changes)
    low1, high1 = one_sided_range(changes)

    verdict = decide(low, high, DELTA)
    verdict_one_sided = decide(low1, high1, DELTA)
    if observed < -DELTA:
        naive = "REGRESSION"
    else:
        naive = "OK"
    needed = estimate_cases_needed(observed, low, high, DELTA, len(cases))
    return observed, low, high, verdict, verdict_one_sided, naive, needed


baseline_records = load_records(file_for(BASELINE_NAME))
print("Delta (biggest drop we accept):", DELTA)
print("Cases:", len(cases))
print("Baseline pass rate:", round(overall_pass_rate(baseline_records), 3),
      "| agent crashes in baseline:", count_errors(baseline_records))
print()

for name in OTHER_NAMES:
    path = file_for(name)
    if not os.path.exists(path):
        print(name, "-> file not found, skipping")
        print()
        continue
    new_records = load_records(path)
    observed, low, high, verdict, verdict_one, naive, needed = compare_two(baseline_records, new_records)
    print(name)
    print("   pass rate:", round(overall_pass_rate(new_records), 3),
          "| agent crashes:", count_errors(new_records))
    print("   average change per case:", round(observed, 3))
    print("   95% range:", round(low, 3), "to", round(high, 3))
    print("   OUR verdict (two-sided):", verdict)
    print("   OUR verdict (one-sided):", verdict_one)
    print("   NAIVE rule:", naive)
    if needed is not None:
        print("   cases needed to settle (rough):", needed)
    print()