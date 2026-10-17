from models import RunRecord


def save_records(records, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(record.model_dump_json() + "\n")


def load_records(file_path):
    records = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "":
                continue

            record = RunRecord.model_validate_json(line)
            records.append(record)

    return records

