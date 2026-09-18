from photonx_eda_pcb.snapshot_store import SnapshotStore,diff_snapshots,validate_snapshot
def test_snapshot_lineage_and_diff():
    s=SnapshotStore();a=s.create('{"a":1}',"one");b=s.create('{"a":2}',"two")
    assert [x.id for x in s.lineage()]==[b.id,a.id]
    assert diff_snapshots(a,b)["changed"]["a"]==(1,2)
    assert validate_snapshot(a)==[]
