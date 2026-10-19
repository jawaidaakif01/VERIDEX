from storage import load_records
from analysis import compare_records

baseline = load_records("results/triage_v0_baseline.jsonl")

for name in ["v1_aa_rerun", "v2_reworded"]:
    other = load_records("results/triage_" + name + ".jsonl")
    result = compare_records(baseline, other, delta=0.05)
    print(name)
    print(result.model_dump_json(indent=2))
    print()

# A deliberate mistake: compare against a file with different cases
print("Now a deliberate mismatch:")
partial = []
for record in baseline:
    if record.case_id != "ticket_30":
        partial.append(record)
try:
    compare_records(baseline, partial)
except ValueError as problem:
    print("  ValueError:", problem)