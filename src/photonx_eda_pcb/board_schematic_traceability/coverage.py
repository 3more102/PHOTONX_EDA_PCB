def traceability_coverage(t):
    if not t.traces:return 1.0
    return round(sum(bool(x.page_ids) for x in t.traces)/len(t.traces),6)
