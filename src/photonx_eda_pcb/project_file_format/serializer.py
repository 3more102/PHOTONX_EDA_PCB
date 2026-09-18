import json
from .model import ProjectFile,ProjectArtifact
def dumps_project(project):
    payload={"name":project.name,"schema_version":project.schema_version,"artifacts":[{"role":a.role,"path":a.path,"sha256":a.sha256,"required":a.required} for a in sorted(project.artifacts,key=lambda x:(x.role,x.path))],"settings":project.settings,"metadata":project.metadata}
    return json.dumps(payload,sort_keys=True,separators=(",",":"))
def loads_project(text):
    d=json.loads(text)
    arts=[ProjectArtifact(str(a["role"]),str(a["path"]),str(a.get("sha256","")),bool(a.get("required",False))) for a in d.get("artifacts",[])]
    return ProjectFile(str(d["name"]),int(d.get("schema_version",1)),arts,dict(d.get("settings",{})),dict(d.get("metadata",{})))
