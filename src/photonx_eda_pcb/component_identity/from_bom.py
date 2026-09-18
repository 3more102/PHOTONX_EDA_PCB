from .model import IdentityCandidate
def candidates_from_bom(items):
    out=[]
    for item in items:
        for r in item.references:out.append(IdentityCandidate(str(r),"unknown",item.value or None,item.footprint or None,item.mpn or None,.99,"bom"))
    return out
