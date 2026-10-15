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