from photonx_eda_pcb.artifact_bundle import build_bundle
from photonx_eda_pcb.artifact_bundle.select import select_entries
def test_bundle_select():
    b=build_bundle("x",[{"path":"a.json","role":"report","content":"a"},{"path":"b.csv","role":"report","content":"b"}])
    assert [x.path for x in select_entries(b,suffixes=(".csv",))]==["b.csv"]
