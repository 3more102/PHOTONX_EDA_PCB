from photonx_eda_pcb.artifact_catalog.artifact import Artifact
from photonx_eda_pcb.artifact_catalog.catalog import ArtifactCatalog
from photonx_eda_pcb.artifact_catalog.lineage import dependency_edges,missing_dependencies

def test_artifact_lineage_detects_missing_input():
    c=ArtifactCatalog();c.add(Artifact('out','json','out.json',inputs=('source',)))
    assert dependency_edges(c)==[('source','out')]
    assert missing_dependencies(c)==['source']
