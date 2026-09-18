from photonx_eda_pcb.dataset_manifest import DatasetFile,DatasetCase,DatasetManifest,validate_dataset_manifest,dataset_fingerprint
from photonx_eda_pcb.dataset_manifest.stats import dataset_stats
def test_dataset_manifest():
    m=DatasetManifest("synthetic","1",[DatasetCase("c",(DatasetFile("a.gbr","gerber_copper","a"*64,10),),True,intentionally_unknown=("original_net_names",))])
    assert validate_dataset_manifest(m)==[]
    assert len(dataset_fingerprint(m))==64
    assert dataset_stats(m)["bytes"]==10
