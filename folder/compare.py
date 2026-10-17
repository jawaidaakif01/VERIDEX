'''
What each function does:

case_pass_rates: for each case, counts the passes and divides by the number of runs. A case that passed 3 of 5 runs gets 0.6.
case_changes: takes the new rate minus the old rate for each case. One number per case, such as -0.2 or 0.4.
average: adds numbers up and divides by how many there are.
one_bootstrap_round: random.randrange(len(changes)) picks a random position in the list. We do that 20 times, collect the picked changes, and average them. Some cases get picked twice and some never, and that’s intended.
'''

import random

def case_pass_rate(all_results):
    '''For each test case, work out its pass rate. Returns a list of numbers.'''

    rates = []
    for results_for_this_case in all_results:
        passed = 0
        for outcome in results_for_this_case:
            passed = passed + outcome
        rate  = passed / len(results_for_this_case)
        rates.append(rate)

    return rates


def case_changes(old_version, new_version):
    '''For each test case, how much did its pass rate change? (new minus old)'''
    old_rates = case_pass_rate(old_version)
    new_rates = case_pass_rate(new_version)

    changes = []

    for i in range(len(old_rates)):
        change = new_rates[i] - old_rates[i]
        changes.append(round(change, 3))
    return changes


def average(numbers):
    '''Add up the numbers and divide by how many there are.'''
    total = 0
    for number in numbers:
        total = total + number

    return total / len(numbers)

def one_bootstrap_round(changes):
    '''Pretend we ran the experiment again.
    Pick test cases at random (the same case can be picked twice),
    then average the changes of the picked cases.
    '''

    picked = []
    for i in range(len(changes)):
        random_position = random.randrange(len(changes))
        picked.append(changes[random_position])
    return average(picked)


def confidence_range(changes, n_rounds = 1000):
    '''Run many bootstrap rounds, then keep the middle 95% of the averages. Returns (low, high).'''
    round_averages = []
    for r in range(n_rounds):
        round_averages.append(one_bootstrap_round(changes))

    round_averages.sort()

    low_position = int(n_rounds * 0.025)
    high_position = int(n_rounds * 0.975) - 1
    return round_averages[low_position], round_averages[high_position]

def one_sided_range(changes, n_rounds = 1000):
    round_averages = []
    for r in range(n_rounds):
        round_averages.append(one_bootstrap_round(changes))

    round_averages.sort()
    low_position = int(n_rounds * 0.05)
    high_position = int(n_rounds * 0.95) - 1
    return round_averages[low_position], round_averages[high_position]


def decide(low, high, delta):
    '''Turn the range into one of three verdicts.
    delta = the size of drop we are willing to accept.
    '''

    if high < -delta:
        return "REGRESSION"
    if low > - delta:
        return "NO_MATERIAL_REGRESSION"
    return "INCONCLUSIVE"


def find_flaky_cases(all_results):
    '''Find test cases that sometimes pass and sometimes fail.
    Returns a list of (case_number, pass_rate). Case numbers start at 1.
    '''

    rates = case_pass_rate(all_results)
    flaky = []
    for i in range(len(rates)):
        if rates[i] > 0 and rates[i] < 1:
            flaky.append((i + 1, rates[i]))
    return flaky

def count_case_types(all_results):
    '''Count how many cases always pass, always fail, or are flaky.
    Returns (always_pass, always_fail, flaky).'''

    rates = case_pass_rate(all_results)
    always_pass = 0
    always_fail = 0
    flaky = 0

    for rate in rates:
        if rate == 1:
            always_pass = always_pass + 1
        elif rate == 0:
            always_fail = always_fail + 1
        else:
            flaky = flaky + 1
    return always_pass, always_fail, flaky


def estimate_cases_needed(observed, low, high, delta, current_cases):
    '''If the verdict is INCONCLUSIVE, roughly hwo many test cases would we need to get a clear answer? Returns None if the verdict is already clear.'''

    if decide(low, high, delta) != "INCONCLUSIVE":
        return None

    half_width = (high-low)/2
    gap = abs(observed - (-delta))

    if gap < 0.005:
        gap = 0.005

    times_more = (half_width / gap) ** 2
    needed = int(current_cases * times_more) + 1
    return needed