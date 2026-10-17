import json


def check_right_tool_called(result, required_tool):
    return required_tool in result.tools_called


def check_valid_format(result, required_keys):
    try:
        data = json.loads(result.output)
    except Exception:
        return False
    if not isinstance(data, dict):
        return False
    for key in required_keys:
        if key not in data:
            return False
    return True


def check_step_limit(result, max_steps):
    return result.steps <= max_steps


def run_all_checks(result, rules):
    failures = []
    if "required_tool" in rules:
        if not check_right_tool_called(result, rules["required_tool"]):
            failures.append("did not call tool '" + rules["required_tool"] + "'")
    if "required_keys" in rules:
        if not check_valid_format(result, rules["required_keys"]):
            failures.append("output is not valid JSON with keys " + str(rules["required_keys"]))
    if "max_steps" in rules:
        if not check_step_limit(result, rules["max_steps"]):
            failures.append("used " + str(result.steps) + " steps, limit is " + str(rules["max_steps"]))
    passed = len(failures) == 0
    return passed, failures