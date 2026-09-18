from .model import IdentityCandidate
def candidates_from_placements(placements):
    return [IdentityCandidate(str(p.reference),"unknown",p.value or None,p.footprint or None,None,.9,"pick_place") for p in placements]
