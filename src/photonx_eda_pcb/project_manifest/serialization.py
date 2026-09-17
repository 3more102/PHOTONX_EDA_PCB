from dataclasses import asdict
from .model import ProjectManifest,SourceFile
def manifest_to_dict(manifest): return asdict(manifest)
def manifest_from_dict(value):
    return ProjectManifest(value["name"],[SourceFile(**item) for item in value.get("sources",[])],dict(value.get("metadata",{})))
