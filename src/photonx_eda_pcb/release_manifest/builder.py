from .model import ReleaseManifest,ReleaseArtifact
def build_release_manifest(version,commit,artifacts,metadata=None):
    items=[ReleaseArtifact(str(a["path"]),str(a["role"]),str(a["sha256"]),int(a.get("size",0))) for a in artifacts]
    items.sort(key=lambda x:(x.role,x.path))
    return ReleaseManifest(str(version),str(commit),items,dict(metadata or {}))
