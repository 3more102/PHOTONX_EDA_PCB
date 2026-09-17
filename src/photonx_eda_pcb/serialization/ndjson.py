import json
def encode_records(records): return "".join(json.dumps(record,sort_keys=True)+"\n" for record in records)
def decode_records(text): return [json.loads(line) for line in str(text).splitlines() if line.strip()]
