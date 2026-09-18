def bus_report(items):
    return [{"name":b.name,"nets":list(b.net_ids),"indices":list(b.indices),"width":b.width,"confidence":b.confidence,"evidence":list(b.evidence)} for b in items]
