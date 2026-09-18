from .coverage import traceability_coverage
def traceability_report(m):return {"coverage":traceability_coverage(m),"links":[{"claim_id":x.claim_id,"sources":list(x.source_ids),"artifacts":list(x.artifact_ids),"reviews":list(x.review_ids),"objects":list(x.object_ids),"confidence":x.confidence} for x in m.links]}
