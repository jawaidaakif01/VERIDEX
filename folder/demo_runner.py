import random
from models import TestCase
from runner import run_all


def fake_agent(question):
    chance = random.random()
    if chance < 0.1:
        raise ValueError("model timed out")
    if chance < 0.75:
        return "Your order ships tomorrow."
    return "Sorry, I do not know."


def check_answer(case, output):
    return case.expected_word in output


cases = [
    TestCase(case_id="case_1", question="Where is my order?", expected_word="ships"),
    TestCase(case_id="case_2", question="When will it arrive?", expected_word="ships"),
    TestCase(case_id="case_3", question="Is my parcel sent?", expected_word="ships"),
]

records = run_all(fake_agent, check_answer, cases, "baseline", n_runs=5)

print("Total records:", len(records))
passed_count = 0
error_count = 0
for record in records:
    if record.passed:
        passed_count = passed_count + 1
    if record.error is not None:
        error_count = error_count + 1
print("Passed:", passed_count)
print("Errors:", error_count)
print()
print("First 3 records:")
for record in records[:3]:
    print(record)