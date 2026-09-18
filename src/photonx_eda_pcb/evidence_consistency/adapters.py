def from_source_observations(items):
    from .model import ClaimObservation
    return [ClaimObservation(x.subject_id,x.field,x.value,x.source,x.confidence,x.source) for x in items]
def from_evidence_items(subject_id,field,items):
    from .model import ClaimObservation
    return [ClaimObservation(str(subject_id),str(field),x.claim,x.source,x.confidence,x.independent_group) for x in items]
