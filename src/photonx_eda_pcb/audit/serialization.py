from dataclasses import asdict
def audit_records_to_dicts(records): return [asdict(record) for record in records]
