from photonx_eda_pcb.assembly_dfm import analyze_assembly_dfm,validate_report
from photonx_eda_pcb.assembly_dfm.score import dfm_score
class C:
    def __init__(self,reference,center,kind="resistor"):self.reference=reference;self.center=center;self.kind=kind
def test_assembly_dfm_edge_and_polarity():
    r=analyze_assembly_dfm([C("U1",(.1,.1),"ic"),C("R1",(5,5))],(0,0,10,10),min_edge_mm=.5,polarity_marked=[])
    codes=[x.code for x in r.findings]
    assert "COMPONENT_EDGE_CLEARANCE" in codes and "POLARITY_MARK_MISSING" in codes
    assert dfm_score(r)<1 and validate_report(r)==[]
