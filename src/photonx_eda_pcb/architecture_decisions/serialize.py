import json
from .model import ArchitectureDecision
def dumps_decisions(items):return json.dumps([{"id":d.id,"title":d.title,"status":d.status,"context":d.context,"decision":d.decision,"consequences":list(d.consequences)} for d in sorted(items,key=lambda x:x.id)],sort_keys=True,separators=(",",":"))
def loads_decisions(text):return [ArchitectureDecision(str(x["id"]),str(x["title"]),str(x["status"]),str(x["context"]),str(x["decision"]),tuple(map(str,x.get("consequences",[])))) for x in json.loads(text)]
