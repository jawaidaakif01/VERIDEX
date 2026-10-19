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


def read_output_data(result):
    try:
        data = json.loads(result.output)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return data


def check_label(result, key, expected_value):
    data = read_output_data(result)
    if data is None:
        return False
    return data.get(key) == expected_value


def check_no_placeholders(result):
    data = read_output_data(result)
    if data is None:
        return False
    draft = data.get("draft_response")
    if draft is None:
        return True
    if "[" in draft and "]" in draft:
        return False
    return True


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
    if "expected_category" in rules:
        if not check_label(result, "category", rules["expected_category"]):
            failures.append("category was not '" + rules["expected_category"] + "'")
    if "expected_priority" in rules:
        if not check_label(result, "priority", rules["expected_priority"]):
            failures.append("priority was not '" + rules["expected_priority"] + "'")
    if rules.get("no_placeholders") is True:
        if not check_no_placeholders(result):
            failures.append("draft contains a [placeholder]")
    passed = len(failures) == 0
    return passed, failures