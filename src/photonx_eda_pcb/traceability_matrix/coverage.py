def traceability_coverage(matrix):
    if not matrix.links:return {"claims":0,"source_coverage":1.0,"artifact_coverage":1.0,"review_coverage":1.0}
    n=len(matrix.links)
    return {"claims":n,"source_coverage":round(sum(bool(x.source_ids) for x in matrix.links)/n,6),"artifact_coverage":round(sum(bool(x.artifact_ids) for x in matrix.links)/n,6),"review_coverage":round(sum(bool(x.review_ids) for x in matrix.links)/n,6)}
