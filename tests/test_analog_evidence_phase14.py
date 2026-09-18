from photonx_eda_pcb.analog_blocks.model import AnalogBlockCandidate
from photonx_eda_pcb.analog_blocks.evidence import analog_evidence_records
from photonx_eda_pcb.analog_blocks.review import analog_review_items
def test_analog_evidence_and_review():
    b=AnalogBlockCandidate("a","rc_filter",("R1","C1"),("N1","GND"),.75,("topology",),(),("function_unproven",))
    e=analog_evidence_records([b])
    assert len(e)==1 and e[0].confidence==.75
    assert analog_review_items([b])
