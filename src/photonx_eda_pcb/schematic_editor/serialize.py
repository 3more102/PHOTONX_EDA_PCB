import json
from .model import *
def dumps_document(doc):
    payload={"pages":[p.__dict__ for p in sorted(doc.pages.values(),key=lambda x:x.id)],"symbols":[s.__dict__ for s in sorted(doc.symbols.values(),key=lambda x:x.id)],"wires":[{"id":w.id,"net_id":w.net_id,"points":[list(p) for p in w.points],"page_id":w.page_id} for w in sorted(doc.wires.values(),key=lambda x:x.id)],"labels":[l.__dict__ for l in sorted(doc.labels.values(),key=lambda x:x.id)],"buses":[{"id":b.id,"name":b.name,"net_ids":list(b.net_ids),"points":[list(p) for p in b.points],"page_id":b.page_id} for b in sorted(doc.buses.values(),key=lambda x:x.id)],"metadata":doc.metadata}
    return json.dumps(payload,sort_keys=True,separators=(",",":"))
def loads_document(text):
    d=json.loads(text);doc=EditorDocument(metadata=dict(d.get("metadata",{})))
    for p in d.get("pages",[]):doc.pages[p["id"]]=EditorPage(p["id"],p["title"],list(p.get("symbol_ids",[])),list(p.get("wire_ids",[])),list(p.get("label_ids",[])),list(p.get("bus_ids",[])))
    for x in d.get("symbols",[]):doc.symbols[x["id"]]=EditorSymbol(**x)
    for x in d.get("wires",[]):doc.wires[x["id"]]=EditorWire(x["id"],x["net_id"],tuple(tuple(map(float,p)) for p in x["points"]),x.get("page_id","root"))
    for x in d.get("labels",[]):doc.labels[x["id"]]=EditorLabel(**x)
    for x in d.get("buses",[]):doc.buses[x["id"]]=EditorBus(x["id"],x["name"],tuple(x["net_ids"]),tuple(tuple(map(float,p)) for p in x["points"]),x.get("page_id","root"))
    return doc
