import json
from .model import Baseline
from .store import BaselineStore
def dumps_baselines(store):return json.dumps([{"id":b.id,"metrics":b.metrics,"tolerances":b.tolerances} for b in store.all()],sort_keys=True,separators=(",",":"))
def loads_baselines(text):
    s=BaselineStore()
    for x in json.loads(text):s.add(Baseline(str(x["id"]),dict(x["metrics"]),dict(x.get("tolerances",{}))))
    return s
