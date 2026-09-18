import json
from .model import EvidenceRecord
from .store import EvidenceDatabase
def dumps_database(db):
    return json.dumps([{"id":r.id,"object_id":r.object_id,"kind":r.kind,"confidence":r.confidence,"source":r.source,"detail":r.detail,"group":r.group} for r in db.all()],sort_keys=True,separators=(",",":"))
def loads_database(text):
    db=EvidenceDatabase()
    for x in json.loads(text):db.add(EvidenceRecord(str(x["id"]),str(x["object_id"]),str(x["kind"]),float(x["confidence"]),str(x.get("source","")),str(x.get("detail","")),str(x.get("group",""))))
    return db
