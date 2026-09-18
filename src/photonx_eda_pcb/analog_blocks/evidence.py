from photonx_eda_pcb.evidence_database.model import EvidenceRecord
import hashlib
def analog_evidence_records(blocks):
    out=[]
    for b in blocks:
        detail=f"kind={b.kind};components={','.join(b.components)};evidence={','.join(b.evidence)}"
        eid="analog:"+hashlib.sha1((b.id+detail).encode()).hexdigest()[:16]
        out.append(EvidenceRecord(eid,b.id,"analog_block_candidate",b.confidence,"analog_blocks",detail,"functional_inference"))
    return out
