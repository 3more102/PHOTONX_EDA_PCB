import json
from .model import Annotation,AnnotationStore
def dumps_annotations(store):
    return json.dumps([{"id":x.id,"object_id":x.object_id,"text":x.text,"author":x.author,"category":x.category,"resolved":x.resolved} for x in sorted(store.items,key=lambda a:a.id)],sort_keys=True,separators=(",",":"))
def loads_annotations(text):
    return AnnotationStore([Annotation(str(x["id"]),str(x["object_id"]),str(x["text"]),str(x.get("author","")),str(x.get("category","note")),bool(x.get("resolved",False))) for x in json.loads(text)])
