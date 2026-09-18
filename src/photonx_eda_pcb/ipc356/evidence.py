from dataclasses import dataclass
@dataclass(frozen=True)
class IpcNetEvidence:
    pad_id:str
    net_name:str
    reference:str|None
    pin:str|None
    confidence:float
def record_to_evidence(record,pad):
    if pad is None or not record.net_name:return None
    score=.7
    if record.reference:score+=.15
    if record.pin:score+=.15
    return IpcNetEvidence(str(pad.id),str(record.net_name),record.reference,record.pin,round(min(score,1),12))
