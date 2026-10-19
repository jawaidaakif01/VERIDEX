import sys
from storage import load_records

file_path = sys.argv[1]
case_id = sys.argv[2]

records = load_records(file_path)
for record in records:
    if record.case_id == case_id:
        print("run", record.run_number, "| passed:", record.passed, "| steps:", record.steps)
        print("   failures:", record.failures)
        print("   output:", record.output[:300])
        print()