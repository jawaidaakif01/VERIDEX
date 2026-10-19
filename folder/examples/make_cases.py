import json

cases = []
for i in range(1, 31):
    cases.append({
        "case_id": "q" + str(i),
        "question": "What is the capital of France? (question " + str(i) + ")",
        "rules": {"contains": ["Paris"], "not_contains": ["not sure"]},
    })

with open("examples/cases.json", "w", encoding="utf-8") as file:
    json.dump(cases, file, indent=2)
print("Wrote", len(cases), "cases to examples/cases.json")