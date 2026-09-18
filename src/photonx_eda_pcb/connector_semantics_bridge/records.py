import hashlib
from photonx_eda_pcb.evidence_database.model import EvidenceRecord
def _r(obj,kind,conf,detail):
    eid="conn:"+hashlib.sha1(f"{obj}|{kind}|{detail}".encode()).hexdigest()[:16]
    return EvidenceRecord(eid,str(obj),kind,float(conf),"connector_semantics",detail,"external_interface")
def pin_function_records(items):return [_r(f"{x.connector_id}:{x.pin}","connector_pin_function",x.confidence,str(x.function)) for x in items if x.function]
def port_records(items):return [_r(x.connector_id,"connector_port",x.confidence,x.kind) for x in items]
