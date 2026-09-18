from photonx_eda_pcb.release_manifest.model import ReleaseArtifact
from photonx_eda_pcb.manufacturing_package import assess_package,pcb_fabrication_profile
def test_missing_outline_blocks_package():
    a=assess_package([ReleaseArtifact("top","copper","a"*64)],pcb_fabrication_profile())
    assert "PACKAGE_MISSING_OUTLINE" in a.blockers and "outline" in a.missing
