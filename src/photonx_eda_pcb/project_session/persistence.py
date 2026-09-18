import json
from .model import ProjectSession
def dump_session(session):
    return json.dumps({"project_name":session.project_name,"root":session.root,"active_board":session.active_board,"open_documents":list(session.open_documents),"settings":session.settings,"dirty":session.dirty,"revision":session.revision},sort_keys=True,separators=(",",":"))
def load_session(text):
    d=json.loads(text)
    return ProjectSession(str(d["project_name"]),str(d.get("root","")),d.get("active_board"),list(d.get("open_documents",[])),dict(d.get("settings",{})),bool(d.get("dirty",False)),int(d.get("revision",0)))
