from .matcher import nearest_pad
from .evidence import record_to_evidence
def map_records_to_pads(records,pads,tolerance_mm=.15):
    evidence=[];unmatched=[]
    for r in records:
        p=nearest_pad(r,pads,tolerance_mm)
        ev=record_to_evidence(r,p)
        if ev:evidence.append(ev)
        else:unmatched.append(r)
    return evidence,unmatched
