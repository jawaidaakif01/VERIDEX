import time
from models import RunRecord


def run_one(agent_function, check_function, case, version, run_number):
    start_time = time.time()
    output = ""
    error = None
    passed = False
    try:
        output = agent_function(case.question)
        passed = check_function(case, output)
    except Exception as problem:
        error = str(problem)
        passed = False
    seconds = time.time() - start_time
    record = RunRecord(
        case_id=case.case_id,
        version=version,
        run_number=run_number,
        passed=passed,
        output=output,
        error=error,
        seconds=seconds,
    )
    return record


def run_all(agent_function, check_function, cases, version, n_runs):
    records = []
    for case in cases:
        for run_number in range(1, n_runs + 1):
            record = run_one(agent_function, check_function, case, version, run_number)
            records.append(record)
    return records