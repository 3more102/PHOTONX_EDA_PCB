import json
from .model import EcoSet,EcoChange
def dumps_eco(e):return json.dumps({"name":e.name,"changes":[x.__dict__ for x in e.changes],"metadata":e.metadata},sort_keys=True,separators=(",",":"))
def loads_eco(text):
    d=json.loads(text);return EcoSet(str(d["name"]),[EcoChange(**x) for x in d.get("changes",[])],dict(d.get("metadata",{})))
