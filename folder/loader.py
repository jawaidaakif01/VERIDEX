import json
import os
import importlib.util
from models import TestCase


def load_agent_function(file_path, function_name="agent"):
    if not os.path.exists(file_path):
        raise ValueError("Agent file not found: " + file_path)
    spec = importlib.util.spec_from_file_location("user_agent_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, function_name):
        raise ValueError("The file " + file_path + " has no function called '" + function_name + "'")
    return getattr(module, function_name)


def load_cases(file_path):
    if not os.path.exists(file_path):
        raise ValueError("Cases file not found: " + file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        items = json.load(file)
    cases = []
    for item in items:
        case = TestCase(
            case_id=item["case_id"],
            question=item["question"],
            rules=item.get("rules", {}),
        )
        cases.append(case)
    return cases