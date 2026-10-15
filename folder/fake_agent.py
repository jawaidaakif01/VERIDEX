import random

def run_fake_agent(pass_chance):
    '''Pretend to run an agent one time. Returns 1 if it passed, 0 if it failed.'''

    if random.random() < pass_chance:
        return 1
    return 0

def run_all_cases(n_cases, n_runs, pass_chance):
    '''Run every test case several times. Returns a list of lists, one list per case.'''
    all_results = []
    for case in range(n_cases):
        results_for_this_case = []
        for run in range(n_runs):
            outcome = run_fake_agent(pass_chance)
            results_for_this_case.append(outcome)
        all_results.append(results_for_this_case)
    return all_results

def pass_rate(all_results):
    '''What fraction of all runs passed?'''

    total_runs = 0
    passed_runs = 0

    for results_for_this_case in all_results:
        for outcome in results_for_this_case:
            total_runs = total_runs + 1
            passed_runs = passed_runs + outcome
    return passed_runs / total_runs


def run_cases_with_chances(chances, n_runs):
    '''Like run_all_cases, but every test case has its own pass chance.
    chances is a list such as [1.0, 0.9, 0.5, 0.0].
    '''

    all_results = []
    for pass_chance in chances:
        results_for_this_case = []
        for run in range(n_runs):
            outcome = run_fake_agent(pass_chance)
            results_for_this_case.append(outcome)
        all_results.append(results_for_this_case)

    return all_results