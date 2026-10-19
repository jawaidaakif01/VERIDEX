import os
from models import TestCase
from demo_agent import make_store, build_graph
from runner import run_all_graph
from storage import save_records, load_records
from bridge import records_to_results
from compare import case_changes, average, confidence_range, decide

DELTA = 0.05

rules = {
    "required_tool": "lookup_order",
    "required_keys": ["status", "message"],
    "max_steps": 5,
}

order_ids = ["A1", "B2", "C3", "D4"]
cases = []
for i in range(1, 41):
    order_id = order_ids[i % 4]
    case = TestCase(case_id="case_" + str(i), question="Where is order " + order_id)
    cases.append(case)

store = make_store()

baseline_graph = build_graph(store, flaky_chance=0.10, seed=11)
new_graph = build_graph(store, flaky_chance=0.30, seed=22)

os.makedirs("results", exist_ok=True)
baseline_records = run_all_graph(baseline_graph, cases, "baseline", 5, store, rules)
save_records(baseline_records, "results/agent_baseline.jsonl")
new_records = run_all_graph(new_graph, cases, "new_version", 5, store, rules)
save_records(new_records, "results/agent_new.jsonl")

old_loaded = load_records("results/agent_baseline.jsonl")
new_loaded = load_records("results/agent_new.jsonl")

old_results = records_to_results(old_loaded, cases)
new_results = records_to_results(new_loaded, cases)

changes = case_changes(old_results, new_results)
observed = average(changes)
low, high = confidence_range(changes)

print("Records saved: baseline", len(old_loaded), "| new", len(new_loaded))
print("Example record:", new_loaded[0])
print()
print("Observed average change:", round(observed, 3))
print("Confidence range:", round(low, 3), "to", round(high, 3))
print("Verdict:", decide(low, high, DELTA))