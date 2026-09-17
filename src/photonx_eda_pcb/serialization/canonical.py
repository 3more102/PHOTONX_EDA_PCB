import json
def dumps_canonical(value): return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
