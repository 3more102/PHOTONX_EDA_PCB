import json
from .model import Snapshot
def dumps_snapshot(s):return json.dumps({"id":s.id,"parent_id":s.parent_id,"payload":s.payload,"sha256":s.sha256,"label":s.label},sort_keys=True,separators=(",",":"))
def loads_snapshot(text):
    d=json.loads(text);return Snapshot(str(d["id"]),d.get("parent_id"),str(d["payload"]),str(d["sha256"]),str(d.get("label","")))
