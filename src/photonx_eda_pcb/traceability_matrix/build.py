from .model import TraceabilityMatrix,TraceLink
def build_traceability_matrix(claims):
    links=[]
    for c in claims:
        links.append(TraceLink(str(c["claim_id"]),tuple(sorted(map(str,c.get("source_ids",())))),tuple(sorted(map(str,c.get("artifact_ids",())))),tuple(sorted(map(str,c.get("review_ids",())))),tuple(sorted(map(str,c.get("object_ids",())))),float(c.get("confidence",0.0))))
    return TraceabilityMatrix(sorted(links,key=lambda x:x.claim_id))
