import os
from demo_runner_parts import fake_agent, check_answer, cases
from runner import run_all
from storage import save_records, load_records



records = run_all(fake_agent, check_answer, cases, "baseline", n_runs=5)


os.makedirs("results", exist_ok=True)
save_records(records, "results/baseline.jsonl")
print("saved", len(records), "records")

loaded = load_records("results/baseline.jsonl")
print("Loaded", len(loaded), "records")


print("Same first record?", records[0] == loaded[0])

all_same = True
for i in range(len(records)):
    if records[i] != loaded[i]:
        all_same = False


print("All records identical after save + load?", all_same)