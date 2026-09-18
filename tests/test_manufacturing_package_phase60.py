from photonx_eda_pcb.release_manifest.model import ReleaseArtifact
from photonx_eda_pcb.manufacturing_package import assess_package,pcb_fabrication_profile
from photonx_eda_pcb.manufacturing_package.completeness import package_completeness
def test_package_requires_core_fab_roles():
    artifacts=[ReleaseArtifact("top.gbr","copper","a"*64),ReleaseArtifact("edge.gbr","outline","b"*64),ReleaseArtifact("drill.drl","drill","c"*64)]
    req=pcb_fabrication_profile();a=assess_package(artifacts,req)
    assert not a.blockers and package_completeness(a,req)==1.0
