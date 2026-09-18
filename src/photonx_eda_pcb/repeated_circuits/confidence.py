def group_confidence(similarities,fingerprint_confidences,geometry_similarity=None):
    sims=list(similarities);fc=list(fingerprint_confidences)
    base=(sum(sims)/len(sims) if sims else 0)*.65+(sum(fc)/len(fc) if fc else 0)*.25
    if geometry_similarity is not None:base+=max(0,min(1,float(geometry_similarity)))*.1
    return round(min(base,1.0),6)
