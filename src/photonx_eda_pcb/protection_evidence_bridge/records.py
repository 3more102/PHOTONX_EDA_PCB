import hashlib
from photonx_eda_pcb.evidence_database.model import EvidenceRecord
def _r(obj,kind,conf,detail):
    eid="prot:"+hashlib.sha1(f"{obj}|{kind}|{detail}".encode()).hexdigest()[:16]
    return EvidenceRecord(eid,str(obj),kind,float(conf),"protection_inference",detail,"protection")
def protection_records(items):return [_r(x.component_id,"protection_candidate",x.confidence,x.kind) for x in items]
def esd_records(items):return [_r(x.interface_net,"esd_network",x.confidence,",".join(x.protection_components)) for x in items]
def input_path_records(items):return [_r(x.connector_id,"input_protection_path",x.confidence,f"target={x.target_id};kinds={','.join(x.kinds)}") for x in items]
