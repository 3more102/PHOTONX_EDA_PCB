from photonx_eda_pcb.evidence_database.model import EvidenceRecord
import hashlib
def _id(kind,obj,detail):return "syn:"+hashlib.sha1(f"{kind}|{obj}|{detail}".encode()).hexdigest()[:16]
def constraint_records(constraint_set):
    out=[]
    for c in constraint_set.constraints:
        d=f"width={c.min_width_mm};clearance={c.clearance_mm};target={c.target_length_mm}"
        out.append(EvidenceRecord(_id("constraint",c.net_id,d),c.net_id,"constraint_candidate",c.confidence,"constraint_synthesis",d,"design_constraints"))
    return out
def peripheral_records(pmap):
    return [EvidenceRecord(_id("peripheral",x.component_id,x.protocol),x.component_id,"peripheral_mapping",x.confidence,"peripheral_mapping",x.protocol,"semantic_interface") for x in pmap.bindings]
def termination_records(items):
    return [EvidenceRecord(_id("termination",x.component_id,x.kind),x.component_id,"termination_candidate",x.confidence,"termination_networks",x.kind,"signal_integrity") for x in items]
