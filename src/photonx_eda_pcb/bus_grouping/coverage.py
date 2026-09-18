def index_coverage(candidate):
    if not candidate.indices:return 0.0
    span=max(candidate.indices)-min(candidate.indices)+1
    return round(len(candidate.indices)/span,6)
