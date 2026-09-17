def span_summary(spans):
    return {'total':len(spans),'proven':sum(s.proven for s in spans),'resolved':sum(s.from_layer is not None and s.to_layer is not None for s in spans),'unresolved':sum(s.from_layer is None for s in spans)}
