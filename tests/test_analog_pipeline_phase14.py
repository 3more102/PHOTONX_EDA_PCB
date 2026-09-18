from photonx_eda_pcb.analog_pattern_pipeline import analyze_analog,validate_analysis
from photonx_eda_pcb.analog_pattern_pipeline.integrate import add_analog_evidence,add_analog_review
from photonx_eda_pcb.evidence_database.store import EvidenceDatabase
from photonx_eda_pcb.review_workflow.model import ReviewQueue
class I:
    def __init__(self,kind,value=None):self.kind=kind;self.value=value
def test_analog_pipeline_integrates():
    ids={"R1":I("resistor","10kΩ"),"R2":I("resistor","10kΩ")}
    pins={"R1":{"1":"VCC","2":"MID"},"R2":{"1":"MID","2":"GND"}}
    a=analyze_analog(ids,pins,power_nets=["VCC"],ground_nets=["GND"])
    assert a.blocks and validate_analysis(a)==[]
    db=EvidenceDatabase();q=ReviewQueue()
    assert add_analog_evidence(db,a)
    add_analog_review(q,a)
    assert len(db)==len(a.evidence_records)
