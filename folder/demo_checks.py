from models import AgentResult
from checks import run_all_checks

rules = {
    "required_tool": "lookup_order",
    "required_keys": ["status", "message"],
    "max_steps": 5,
}

good = AgentResult(
    output='{"status": "shipped", "message": "Your order ships tomorrow."}',
    tools_called=["lookup_order"],
    steps=3,
)

forgot_tool = AgentResult(
    output='{"status": "shipped", "message": "Probably shipped."}',
    tools_called=[],
    steps=2,
)

bad_format = AgentResult(
    output="Your order ships tomorrow.",
    tools_called=["lookup_order"],
    steps=3,
)

too_many_steps = AgentResult(
    output='{"status": "shipped", "message": "Done."}',
    tools_called=["lookup_order"],
    steps=9,
)

everything_wrong = AgentResult(
    output="no idea",
    tools_called=[],
    steps=12,
)

all_results = [
    ("good", good),
    ("forgot_tool", forgot_tool),
    ("bad_format", bad_format),
    ("too_many_steps", too_many_steps),
    ("everything_wrong", everything_wrong),
]

for name, result in all_results:
    passed, failures = run_all_checks(result, rules)
    if passed:
        print(name, "-> PASS")
    else:
        print(name, "-> FAIL")
    for failure in failures:
        print("     -", failure)