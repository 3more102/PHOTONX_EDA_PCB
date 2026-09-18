from .model import IdentityCandidate
def candidates_from_components(components):
    return [IdentityCandidate(str(c.id),str(c.kind),None,None,None,float(c.confidence),"geometry") for c in components]
