from models import TestCase, RunRecord

case = TestCase(case_id="case_1", question="Where is my order?")
print(case)

record = RunRecord(
    case_id="case_1",
    version="baseline",
    run_number=1,
    passed=True,
    output="Your order ships tomorrow.",
    seconds=0.42,
)
print(record)

# Turn it into one line of JSON text (we will save lines like this)
line = record.model_dump_json()
print(line)

# Turn the line back into a record
same_record = RunRecord.model_validate_json(line)
print(same_record.passed)

# Now give it a wrong type on purpose
bad_record = RunRecord(
    case_id="case_1",
    version="baseline",
    run_number="not a number",
    passed=True,
    output="hi",
    seconds=0.1,
)