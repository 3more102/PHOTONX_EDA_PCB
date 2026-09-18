from photonx_eda_pcb.evidence_database.model import EvidenceRecord
import hashlib
def evidence_records(groups):
    out=[]
    for g in groups:
        for inst in g.instances:
            detail=f"group={g.id};similarity={inst.similarity};differences={','.join(inst.differences)}"
            eid="repeat:"+hashlib.sha1((inst.id+detail).encode()).hexdigest()[:16]
            out.append(EvidenceRecord(eid,inst.seed,"repeated_circuit",g.confidence,"repeated_circuits",detail,"structural_pattern"))
    return out
