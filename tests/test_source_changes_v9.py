from photonx_eda_pcb.source_changes import SourceState,compare_sources,validate_change_set
from photonx_eda_pcb.source_changes.impact import impacted_domains
def test_source_changes_and_impact():
    a=[SourceState("top.gbr","a"*64,10,"gerber_copper"),SourceState("old.drl","b"*64,5,"excellon")]
    b=[SourceState("top.gbr","c"*64,11,"gerber_copper"),SourceState("new.ipc","d"*64,7,"ipc356")]
    cs=compare_sources(a,b)
    assert [x.change_type for x in cs.changes]==["added","removed","modified"]
    mod=[x for x in cs.changes if x.path=="top.gbr"][0]
    assert "connectivity" in impacted_domains(mod)
    assert validate_change_set(cs)==[]
