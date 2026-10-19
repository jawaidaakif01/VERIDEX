import random


def agent(question):
    if random.random() < 0.6:
        return "The answer is: Paris."
    return "I am not sure."