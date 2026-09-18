from photonx_eda_pcb.dataset_manifest import DatasetFile,DatasetCase,DatasetManifest,validate_dataset_manifest
def test_external_dataset_requires_source_and_license():
    m=DatasetManifest("x","1",[DatasetCase("c",(DatasetFile("a","x"),),False)])
    issues=validate_dataset_manifest(m)
    assert "DATASET_EXTERNAL_SOURCE_REQUIRED" in issues and "DATASET_EXTERNAL_LICENSE_REQUIRED" in issues
