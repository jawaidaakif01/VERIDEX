import time
from models import RunRecord
from adapter import run_langgraph_agent
from checks import run_all_checks


INFRA_WORDS = [
    "429", "RESOURCE_EXHAUSTED", "502", "503", "504", "UNAVAILABLE",
    "RemoteProtocolError", "ConnectError", "ConnectTimeout", "ReadTimeout",
    "getaddrinfo", "Server disconnected", "ConnectionError", "Timeout",
]


class InfraError(Exception):
    pass


def looks_like_daily_limit(message):
    for word in ["PerDay", "per day", "TPD"]:
        if word in message:
            return True
    return False


def looks_like_infra_error(message):
    for word in INFRA_WORDS:
        if word in message:
            return True
    return False


def run_one_graph(graph, case, version, run_number, store, rules,
                  input_key="question", output_keys=None,
                  max_attempts=5, retry_wait_seconds=20):
    output = ""
    error = None
    passed = False
    tools_called = []
    steps = 0
    failures = []
    all_rules = dict(rules)
    all_rules.update(case.rules)

    attempt = 1
    while True:
        start_time = time.perf_counter()
        try:
            result = run_langgraph_agent(graph, case.question, store,
                                         input_key=input_key, output_keys=output_keys)
            output = result.output
            tools_called = result.tools_called
            steps = result.steps
            passed, failures = run_all_checks(result, all_rules)
            break
        except Exception as problem:
            message = type(problem).__name__ + ": " + str(problem)
            if looks_like_infra_error(message):
                if looks_like_daily_limit(message):
                    raise InfraError("Daily limit reached, waiting will not help. " + message[:200])
                if attempt >= max_attempts:
                    raise InfraError("Gave up after " + str(attempt) + " attempts: " + message[:200])
                print("   (rate limit or server problem - waiting", retry_wait_seconds,
                      "seconds, attempt", attempt, "of", max_attempts, ")")
                time.sleep(retry_wait_seconds)
                attempt = attempt + 1
            else:
                error = message
                passed = False
                break
    seconds = time.perf_counter() - start_time
    record = RunRecord(
        case_id=case.case_id,
        version=version,
        run_number=run_number,
        passed=passed,
        output=output,
        error=error,
        seconds=seconds,
        tools_called=tools_called,
        steps=steps,
        failures=failures,
    )
    return record


def run_all_graph(graph, cases, version, n_runs, store, rules,
                  input_key="question", output_keys=None, pause_seconds=0,
                  max_attempts=5, retry_wait_seconds=20):
    records = []
    for case in cases:
        for run_number in range(1, n_runs + 1):
            record = run_one_graph(graph, case, version, run_number, store, rules,
                                   input_key=input_key, output_keys=output_keys,
                                   max_attempts=max_attempts,
                                   retry_wait_seconds=retry_wait_seconds)
            records.append(record)
            if pause_seconds > 0:
                time.sleep(pause_seconds)
    return records