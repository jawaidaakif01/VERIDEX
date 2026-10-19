import os
import warnings
warnings.filterwarnings("ignore", message=".*fixed sampling defaults.*")

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from triage_eval import build_triage_graph
from triage_cases import cases
from runner import run_all_graph
from storage import save_records

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")
graph = build_triage_graph(llm)

rules = {"max_steps": 5, "no_placeholders": True}
output_keys = ["category", "priority", "draft_response", "revision_count", "approved"]
N_RUNS = 3

records = run_all_graph(graph, cases, "baseline", N_RUNS, None, rules,
                        input_key="ticket_text", output_keys=output_keys,
                        pause_seconds=1)

os.makedirs("results", exist_ok=True)
save_records(records, "results/triage_baseline.jsonl")

print("Total records:", len(records))
error_count = 0
for record in records:
    if record.error is not None:
        error_count = error_count + 1
print("Runs that crashed (errors):", error_count)
print()

for case in cases:
    passes = 0
    reasons = []
    for record in records:
        if record.case_id == case.case_id:
            if record.passed:
                passes = passes + 1
            for failure in record.failures:
                if failure not in reasons:
                    reasons.append(failure)
            if record.error is not None and record.error not in reasons:
                reasons.append(record.error)
    print(case.case_id, "->", passes, "of", N_RUNS, "passed", reasons)