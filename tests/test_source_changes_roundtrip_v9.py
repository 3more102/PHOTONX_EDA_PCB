from photonx_eda_pcb.source_changes import SourceState,compare_sources
from photonx_eda_pcb.source_changes.serialize import dumps_changes,loads_changes
def test_change_set_roundtrip():
    cs=compare_sources([SourceState("a","a"*64)],[SourceState("a","b"*64)])
    q=loads_changes(dumps_changes(cs))
    assert q.changes==cs.changes
