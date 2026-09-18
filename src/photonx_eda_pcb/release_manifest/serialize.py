import json
from .model import ReleaseManifest,ReleaseArtifact
def dumps_manifest(m):
    return json.dumps({"version":m.version,"commit":m.commit,"artifacts":[a.__dict__ for a in m.artifacts],"metadata":m.metadata},sort_keys=True,separators=(",",":"))
def loads_manifest(text):
    d=json.loads(text);return ReleaseManifest(str(d["version"]),str(d["commit"]),[ReleaseArtifact(**a) for a in d.get("artifacts",[])],dict(d.get("metadata",{})))
