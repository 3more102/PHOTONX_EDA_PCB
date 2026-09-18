import json
from .model import SourceState,SourceChange,ChangeSet
def dumps_changes(cs):
    def state(x):return None if x is None else {"path":x.path,"sha256":x.sha256,"size":x.size,"role":x.role}
    return json.dumps([{"path":c.path,"change_type":c.change_type,"before":state(c.before),"after":state(c.after)} for c in cs.changes],sort_keys=True,separators=(",",":"))
def loads_changes(text):
    def state(x):return None if x is None else SourceState(str(x["path"]),str(x["sha256"]),int(x.get("size",0)),str(x.get("role","unknown")))
    return ChangeSet([SourceChange(str(x["path"]),str(x["change_type"]),state(x.get("before")),state(x.get("after"))) for x in json.loads(text)])
