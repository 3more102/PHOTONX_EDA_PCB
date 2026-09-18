from dataclasses import dataclass
@dataclass(frozen=True)
class RepeatedBlockCandidate:
    id:str
    child_groups:tuple[str,...]
    shared_components:tuple[str,...]
    confidence:float
def repeated_block_candidates(groups):
    out=[]
    for i,a in enumerate(groups):
        ca=set(c for inst in a.instances for c in inst.components)
        for b in groups[i+1:]:
            cb=set(c for inst in b.instances for c in inst.components);shared=tuple(sorted(ca&cb))
            if shared:
                out.append(RepeatedBlockCandidate(f"hier:{a.id}:{b.id}",(a.id,b.id),shared,round(min(a.confidence,b.confidence)*.6,6)))
    return out
