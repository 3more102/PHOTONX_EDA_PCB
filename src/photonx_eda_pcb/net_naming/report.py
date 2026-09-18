def names_report(items):
    return [{"net_id":x.net_id,"name":x.name,"confidence":x.confidence,"sources":list(x.sources),"conflicts":list(x.conflicts)} for x in items]
