from photonx_eda_pcb.query_engine.parser import parse_query
from photonx_eda_pcb.query_engine.compose import and_filter
def test_and_filter():
    items=[{"name":"VCC","w":.5},{"name":"SIG","w":.2},{"name":"VDD","w":.1}]
    out=and_filter(items,parse_query("name~V"),parse_query("w>0.15"))
    assert [x["name"] for x in out]==["VCC"]
