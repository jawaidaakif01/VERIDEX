def records_to_results(records, cases):
    all_results = []
    for case in cases:
        results_for_this_case = []
        for record in records:
            if record.case_id == case.case_id:
                if record.passed:
                    results_for_this_case.append(1)

                else:
                    results_for_this_case.append(0)

        all_results.append(results_for_this_case)
    return all_results
