import os
from triage_run import run_triage_version
from triage_versions import VERSIONS
from triage_eval import DEFAULT_CLASSIFY_PROMPT, DEFAULT_DRAFT_PROMPT

N_RUNS = 3


def run_all(llm=None):
    for version in VERSIONS:
        name = version["name"]
        file_path = "results/triage_" + name + ".jsonl"
        if os.path.exists(file_path):
            print("SKIP", name, "- file already exists")
            continue
        print("=== RUNNING", name, "===")
        run_triage_version(
            name,
            N_RUNS,
            classify_prompt=version.get("classify_prompt", DEFAULT_CLASSIFY_PROMPT),
            draft_prompt=version.get("draft_prompt", DEFAULT_DRAFT_PROMPT),
            llm=llm,
        )
        print()


if __name__ == "__main__":
    run_all()