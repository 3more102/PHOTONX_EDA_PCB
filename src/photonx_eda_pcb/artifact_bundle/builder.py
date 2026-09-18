from .model import BundleEntry,ArtifactBundle
from .hash import content_hash
def build_bundle(name,artifacts,metadata=None):
    entries=[BundleEntry(str(a["path"]),str(a.get("role","artifact")),str(a.get("content","")),content_hash(a.get("content",""))) for a in artifacts]
    entries.sort(key=lambda x:x.path)
    return ArtifactBundle(str(name),entries,dict(metadata or {}))
