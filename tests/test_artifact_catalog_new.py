from photonx_eda_pcb.artifact_catalog.artifact import Artifact
from photonx_eda_pcb.artifact_catalog.catalog import ArtifactCatalog
from photonx_eda_pcb.artifact_catalog.manifest import catalog_manifest

def test_artifact_catalog_orders_names():
    c=ArtifactCatalog();c.add(Artifact('b','json','b.json'));c.add(Artifact('a','source','a.gbr'))
    assert c.names()==['a','b']
    assert [x['name'] for x in catalog_manifest(c)['artifacts']]==['a','b']
