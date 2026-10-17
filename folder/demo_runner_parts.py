import random
from models import TestCase


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