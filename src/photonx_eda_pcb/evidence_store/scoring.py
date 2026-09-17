def combined_confidence(records):
    items=list(records)
    if not items:return 0.0
    residual=1.0
    for record in items: residual*=1.0-record.confidence
    return max(0.0,min(1.0,1.0-residual))
