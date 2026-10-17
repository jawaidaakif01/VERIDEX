import os
import random
from models import TestCase
from runner import run_all
from storage import save_records, load_records
from bridge import records_to_results
from compare import case_changes, average, confidence_range, decide

DELTA = 0.05

def baseline_agent(question):
    if random.random() < 0.85:
        return "Your order ships tomorrow."
    return "Sorry, I do not know."

def new_agent(question):
    if random.random() < 0.70:
        return "Your order ships tomorrow."
    return "Sorry, I do not know."

def check_answer(case, output):
    return case.expected_word in output

cases = []

for i in range(1, 31):
    case = TestCase(case_id="case_" + str(i), question="Question" + str(i), expected_word="ships")
    cases.append(case)

random.seed(1)
os.makedirs("results", exist_ok=True)

baseline_records = run_all(baseline_agent, check_answer, cases, "baseline", n_runs=5)
save_records(baseline_records, "results/baseline.jsonl")

new_records = run_all(new_agent, check_answer, cases, "new_version", n_runs=5)
save_records(new_records, "results/new_version.jsonl")

old_loaded = load_records("results/baseline.jsonl")
new_loaded = load_records("results/new_version.jsonl")

old_results = records_to_results(old_loaded, cases)
new_results = records_to_results(new_loaded, cases)


changes = case_changes(old_results, new_results)
observed = average(changes)
low, high = confidence_range(changes)
verdict = decide(low, high, DELTA)

print("Cases:", len(cases), "| runs per case: 5")
print("Observed average change:", round(observed, 3))
print("Confidence range:", round(low, 3), "to", round(high, 3))
print("Delta:", DELTA)
print("Verdict:", verdict)