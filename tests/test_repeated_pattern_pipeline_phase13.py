import networkx as nx
from photonx_eda_pcb.repeated_pattern_pipeline import analyze_repeated_patterns,validate_analysis
class I:
    def __init__(self,kind):self.kind=kind
def test_pipeline_detects_repeat_channel_and_pattern():
    g=nx.Graph();g.add_edges_from([("C:R1","N:A"),("N:A","C:D1"),("C:R2","N:B"),("N:B","C:D2")])
    for n in g.nodes:g.nodes[n]["kind"]="component" if n.startswith("C:") else "net"
    ids={"R1":I("resistor"),"D1":I("led"),"R2":I("resistor"),"D2":I("led")}
    a=analyze_repeated_patterns(g,["R1","R2"],ids,{})
    assert len(a.repeated_groups)==1 and a.channels[0].kind=="led_driver"
    assert any(x.pattern=="led_resistor_channel" for x in a.pattern_matches)
    assert len(a.evidence_records)==2
    assert validate_analysis(a)==[]
