import json
from .model import GroundTruthCase
def dumps_cases(cases):return json.dumps([{"id":c.id,"expected":c.expected,"observed":c.observed,"tolerances":c.tolerances} for c in sorted(cases,key=lambda x:x.id)],sort_keys=True,separators=(",",":"))
def loads_cases(text):return [GroundTruthCase(str(x["id"]),dict(x["expected"]),dict(x["observed"]),dict(x.get("tolerances",{}))) for x in json.loads(text)]
