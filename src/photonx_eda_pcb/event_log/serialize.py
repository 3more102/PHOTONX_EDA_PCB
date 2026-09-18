import json
from .model import Event
def dumps_events(events):
    return json.dumps([{"seq":e.seq,"kind":e.kind,"message":e.message,"source":e.source,"object_id":e.object_id,"data":e.data} for e in events],sort_keys=True,separators=(",",":"))
def loads_events(text):
    return [Event(int(x["seq"]),str(x["kind"]),str(x["message"]),str(x.get("source","")),x.get("object_id"),dict(x.get("data",{}))) for x in json.loads(text)]
