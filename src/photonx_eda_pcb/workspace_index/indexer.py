from .model import IndexedArtifact,WorkspaceIndex
def build_index(entries):
    out=[]
    for x in entries:
        out.append(IndexedArtifact(str(x["path"]),str(x.get("role","unknown")),int(x.get("size",0)),str(x.get("sha256","")),tuple(sorted(map(str,x.get("tags",()))))))
    out.sort(key=lambda a:(a.role,a.path))
    return WorkspaceIndex(out,{"count":len(out)})
