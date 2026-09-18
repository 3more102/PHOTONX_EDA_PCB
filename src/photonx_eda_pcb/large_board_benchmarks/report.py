import json
def benchmark_suite_json(results):return json.dumps(list(results),sort_keys=True,indent=2)
