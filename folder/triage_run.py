import os
import warnings
from triage_eval import (build_triage_graph, DEFAULT_CLASSIFY_PROMPT,
                         DEFAULT_DRAFT_PROMPT, DEFAULT_CHECK_PROMPT)
from triage_cases import cases
from runner import run_all_graph
from storage import save_records
from bridge import records_to_results
from compare import count_case_types

RULES = {"max_steps": 5, "no_placeholders": True}
OUTPUT_KEYS = ["category", "priority", "draft_response", "revision_count", "approved"]


def make_groq():
    warnings.filterwarnings("ignore", message=".*fixed sampling defaults.*")
    from dotenv import load_dotenv
    from langchain_groq import ChatGroq
    load_dotenv()
    return ChatGroq(model="openai/gpt-oss-120b")


def run_triage_version(version_name, n_runs, classify_prompt=DEFAULT_CLASSIFY_PROMPT,
                       draft_prompt=DEFAULT_DRAFT_PROMPT, check_prompt=DEFAULT_CHECK_PROMPT,
                       llm=None):
    if llm is None:
        llm = make_groq()
    graph = build_triage_graph(llm, classify_prompt, draft_prompt, check_prompt)

    records = run_all_graph(graph, cases, version_name, n_runs, None, RULES,
                            input_key="ticket_text", output_keys=OUTPUT_KEYS,
                            pause_seconds=1)

    os.makedirs("results", exist_ok=True)
    file_path = "results/triage_" + version_name + ".jsonl"
    save_records(records, file_path)

    passed_runs = 0
    error_runs = 0
    for record in records:
        if record.passed:
            passed_runs = passed_runs + 1
        if record.error is not None:
            error_runs = error_runs + 1

    all_results = records_to_results(records, cases)
    always_pass, always_fail, flaky = count_case_types(all_results)

    print("Version:", version_name, "| saved to", file_path)
    print("Total runs:", len(records), "| crashed:", error_runs)
    print("Overall pass rate:", round(passed_runs / len(records), 3))
    print("Cases that always pass:", always_pass, "| always fail:", always_fail, "| flaky:", flaky)
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
        print(case.case_id, "->", passes, "of", n_runs, "passed", reasons)
    return records