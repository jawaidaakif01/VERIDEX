from typing import List, Optional
from pydantic import BaseModel
from compare import (case_changes, average, confidence_range, one_sided_range,
                     decide, estimate_cases_needed)


class ChangedCase(BaseModel):
    case_id: str
    old_rate: float
    new_rate: float
    reasons: List[str] = []

class ComparisonResult(BaseModel):
    n_cases: int
    old_pass_rate: float
    new_pass_rate: float
    observed_change: float
    low: float
    high: float
    delta: float
    verdict: str
    verdict_one_sided: str
    naive_verdict: str
    cases_needed: Optional[int] = None
    flaky_cases: List[str] = []
    changed_cases: List[ChangedCase] = []


def get_case_ids(records):
    case_ids = []
    for record in records:
        if record.case_id not in case_ids:
            case_ids.append(record.case_id)
    return case_ids


def results_by_case(records, case_ids):
    all_results = []
    for case_id in case_ids:
        results_for_this_case = []
        for record in records:
            if record.case_id == case_id:
                if record.passed:
                    results_for_this_case.append(1)
                else:
                    results_for_this_case.append(0)
        if len(results_for_this_case) == 0:
            raise ValueError("No records for case " + case_id)
        all_results.append(results_for_this_case)
    return all_results


def overall_pass_rate(all_results):
    total = 0
    passed = 0
    for results_for_this_case in all_results:
        for outcome in results_for_this_case:
            total = total + 1
            passed = passed + outcome
    return passed / total


def find_flaky_case_ids(case_ids, all_results):
    flaky = []
    for i in range(len(case_ids)):
        passed = 0
        for outcome in all_results[i]:
            passed = passed + outcome
        if passed > 0 and passed < len(all_results[i]):
            flaky.append(case_ids[i])
    return flaky


def collect_reasons(records, case_id):
    reasons = []
    for record in records:
        if record.case_id == case_id:
            for failure in record.failures:
                if failure not in reasons:
                    reasons.append(failure)
            if record.error is not None and record.error not in reasons:
                reasons.append(record.error)
    return reasons


def get_change(changed_case):
    return changed_case.new_rate - changed_case.old_rate


def find_changed_cases(case_ids, old_results, new_results, new_records):
    changed = []
    for i in range(len(case_ids)):
        old_rate = average(old_results[i])
        new_rate = average(new_results[i])
        if abs(new_rate - old_rate) > 0.0001:
            changed.append(ChangedCase(
                case_id=case_ids[i],
                old_rate=round(old_rate, 3),
                new_rate=round(new_rate, 3),
                reasons=collect_reasons(new_records, case_ids[i]),
            ))
    changed.sort(key=get_change)
    return changed


def compare_records(old_records, new_records, delta=0.05, n_rounds=1000):
    case_ids = get_case_ids(old_records)
    new_ids = get_case_ids(new_records)

    missing = []
    for case_id in case_ids:
        if case_id not in new_ids:
            missing.append(case_id)
    extra = []
    for case_id in new_ids:
        if case_id not in case_ids:
            extra.append(case_id)
    if len(missing) > 0 or len(extra) > 0:
        raise ValueError("The two files must contain the same cases. Missing in new: "
                         + str(missing) + " | only in new: " + str(extra))

    old_results = results_by_case(old_records, case_ids)
    new_results = results_by_case(new_records, case_ids)

    changes = case_changes(old_results, new_results)
    observed = average(changes)
    low, high = confidence_range(changes, n_rounds=n_rounds)
    low1, high1 = one_sided_range(changes, n_rounds=n_rounds)

    verdict = decide(low, high, delta)
    verdict_one_sided = decide(low1, high1, delta)
    if observed < -delta:
        naive = "REGRESSION"
    else:
        naive = "OK"
    needed = estimate_cases_needed(observed, low, high, delta, len(case_ids))

    flaky_old = find_flaky_case_ids(case_ids, old_results)
    flaky_new = find_flaky_case_ids(case_ids, new_results)
    flaky_all = []
    for case_id in case_ids:
        if case_id in flaky_old or case_id in flaky_new:
            flaky_all.append(case_id)

    return ComparisonResult(
        n_cases=len(case_ids),
        old_pass_rate=overall_pass_rate(old_results),
        new_pass_rate=overall_pass_rate(new_results),
        observed_change=observed,
        low=low,
        high=high,
        delta=delta,
        verdict=verdict,
        verdict_one_sided=verdict_one_sided,
        naive_verdict=naive,
        cases_needed=needed,
        flaky_cases=flaky_all,
        changed_cases=find_changed_cases(case_ids, old_results, new_results, new_records),
    )



def explain(result):
    delta = str(result.delta)
    if result.verdict == "REGRESSION":
        return ("Even the best end of the range (" + str(round(result.high, 3))
                + ") is worse than -" + delta
                + ". We are confident the drop is bigger than you accept.")
    if result.verdict == "NO_MATERIAL_REGRESSION":
        return ("Even the worst end of the range (" + str(round(result.low, 3))
                + ") is better than -" + delta
                + ". Any drop is smaller than you accept.")
    text = ("The range (" + str(round(result.low, 3)) + " to " + str(round(result.high, 3))
            + ") crosses -" + delta + ", so we cannot tell yet.")
    if result.cases_needed is not None:
        if result.cases_needed > 1000:
            text = (text + " The change sits very close to your delta, so settling it would take a very large experiment (rough guess: "
                    + str(result.cases_needed) + " cases).")
        else:
            text = text + " Roughly " + str(result.cases_needed) + " cases would be needed to settle it."
    return text