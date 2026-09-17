def disconnected_objects(result):
    connected={x for e in result.edges for x in (e.a,e.b)}
    return sorted(x for g in result.groups for x in g if x not in connected)
def low_confidence_edges(result,threshold=0.5):return [e for e in result.edges if e.confidence<threshold]
def diagnostic_summary(result):
    from collections import Counter
    return dict(Counter(x.get('code','UNKNOWN') for x in result.diagnostics))
