import json
from .model import CompatibilityEntry,CompatibilityMatrix
def dumps_matrix(m):return json.dumps([{"feature":e.feature,"format":e.format,"status":e.status,"notes":e.notes,"tests":list(e.tests)} for e in sorted(m.entries,key=lambda x:(x.feature,x.format))],sort_keys=True,separators=(",",":"))
def loads_matrix(text):return CompatibilityMatrix([CompatibilityEntry(str(x["feature"]),str(x["format"]),str(x["status"]),str(x.get("notes","")),tuple(map(str,x.get("tests",[])))) for x in json.loads(text)])
