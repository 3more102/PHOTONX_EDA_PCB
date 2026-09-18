from .model import ReferenceCandidate
from .normalize import normalize_reference
def from_placements(placements):
    return [ReferenceCandidate(str(p.reference),normalize_reference(p.reference),.99,"pick_place") for p in placements if normalize_reference(p.reference)]
def from_bom_items(items):
    out=[]
    for item in items:
        for r in item.references:
            nr=normalize_reference(r)
            if nr:out.append(ReferenceCandidate(nr,nr,.99,"bom"))
    return out
