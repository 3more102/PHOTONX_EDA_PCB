import json
from .model import DatasetManifest,DatasetCase,DatasetFile
def dumps_manifest(m):
    return json.dumps({"name":m.name,"version":m.version,"cases":[{"id":c.id,"synthetic":c.synthetic,"license":c.license,"source":c.source,"intentionally_unknown":list(c.intentionally_unknown),"files":[f.__dict__ for f in c.files]} for c in sorted(m.cases,key=lambda x:x.id)]},sort_keys=True,separators=(",",":"))
def loads_manifest(text):
    d=json.loads(text);cases=[]
    for c in d.get("cases",[]):cases.append(DatasetCase(str(c["id"]),tuple(DatasetFile(**f) for f in c.get("files",[])),bool(c.get("synthetic",True)),str(c.get("license","")),str(c.get("source","")),tuple(map(str,c.get("intentionally_unknown",[])))))
    return DatasetManifest(str(d["name"]),str(d["version"]),cases)
