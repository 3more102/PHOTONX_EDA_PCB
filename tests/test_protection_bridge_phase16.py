from photonx_eda_pcb.protection_inference.model import ProtectionCandidate
from photonx_eda_pcb.esd_networks.model import EsdNetwork
from photonx_eda_pcb.protection_evidence_bridge import protection_records,esd_records,protection_review_items
from photonx_eda_pcb.protection_evidence_bridge.validation import validate_records
def test_protection_evidence_bridge():
    p=[ProtectionCandidate("D1","tvs",("USB","GND"),.7,(),())]
    n=[EsdNetwork("USB",("D1",),("GND",),.85,())]
    records=protection_records(p)+esd_records(n)
    assert validate_records(records)==[]
    assert protection_review_items(p)[0].kind=="protection_hypothesis"
