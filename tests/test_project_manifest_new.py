from photonx_eda_pcb.project_manifest import ProjectManifest,SourceFile,validate_manifest
from photonx_eda_pcb.project_manifest.serialization import manifest_from_dict,manifest_to_dict
def test_manifest_roundtrip():
    manifest=ProjectManifest("demo",[SourceFile("top.gbr","top_copper","abc")],{"owner":"test"})
    restored=manifest_from_dict(manifest_to_dict(manifest))
    assert restored.name=="demo" and restored.sources[0].role=="top_copper" and not validate_manifest(restored)
