import networkx as nx
from photonx_eda_pcb.repeated_pattern_pipeline import analyze_repeated_patterns
from photonx_eda_pcb.repeated_pattern_pipeline.evidence import add_analysis_evidence
from photonx_eda_pcb.repeated_pattern_pipeline.review import add_analysis_review
from photonx_eda_pcb.evidence_database.store import EvidenceDatabase
from photonx_eda_pcb.review_workflow.model import ReviewQueue
class I:
    def __init__(self,kind):self.kind=kind
def test_analysis_integrates_with_evidence_store():
    g=nx.Graph();g.add_edges_from([("C:R1","N:A"),("N:A","C:X1"),("C:R2","N:B"),("N:B","C:X2")])
    for n in g.nodes:g.nodes[n]["kind"]="component" if n.startswith("C:") else "net"
    ids={"R1":I("resistor"),"X1":I("unknown"),"R2":I("resistor"),"X2":I("unknown")}
    a=analyze_repeated_patterns(g,["R1","R2"],ids,{})
    db=EvidenceDatabase();q=ReviewQueue()
    assert len(add_analysis_evidence(db,a))==2 and len(db)==2
    add_analysis_review(q,a)
    assert isinstance(q.items,list)
