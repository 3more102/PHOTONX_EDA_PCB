import json
from .model import ReviewCheckpoint,CheckpointDecision
def dumps_checkpoint(c):
    return json.dumps({"id":c.id,"title":c.title,"required_items":list(c.required_items),"decisions":[d.__dict__ for d in c.decisions],"closed":c.closed},sort_keys=True,separators=(",",":"))
def loads_checkpoint(text):
    d=json.loads(text)
    return ReviewCheckpoint(str(d["id"]),str(d["title"]),tuple(map(str,d.get("required_items",[]))),[CheckpointDecision(**x) for x in d.get("decisions",[])],bool(d.get("closed",False)))
