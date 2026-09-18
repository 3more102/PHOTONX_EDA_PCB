from photonx_eda_pcb.snapshot_store.tags import SnapshotTags
def test_snapshot_tags():
    t=SnapshotTags();t.set("golden","abc");assert t.get("golden")=="abc" and t.all()=={"golden":"abc"}
