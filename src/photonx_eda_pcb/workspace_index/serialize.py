import json
from .model import IndexedArtifact,WorkspaceIndex
def dumps_index(index):
    return json.dumps({"artifacts":[{"path":a.path,"role":a.role,"size":a.size,"sha256":a.sha256,"tags":list(a.tags)} for a in index.artifacts],"metadata":index.metadata},sort_keys=True,separators=(",",":"))
def loads_index(text):
    d=json.loads(text)
    return WorkspaceIndex([IndexedArtifact(str(a["path"]),str(a["role"]),int(a.get("size",0)),str(a.get("sha256","")),tuple(map(str,a.get("tags",[])))) for a in d.get("artifacts",[])],dict(d.get("metadata",{})))
