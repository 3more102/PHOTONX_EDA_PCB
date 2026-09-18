from photonx_eda_pcb.workspace_index import build_index,search_index,validate_index
from photonx_eda_pcb.workspace_index.stats import index_stats
def test_workspace_index():
    idx=build_index([{"path":"fab/top.gbr","role":"gerber_copper","size":10,"tags":["top"]},{"path":"asm/bom.csv","role":"bom","size":5}])
    assert [x.path for x in search_index(idx,role="bom")]==["asm/bom.csv"]
    assert index_stats(idx)["bytes"]==15
    assert validate_index(idx)==[]
