def references_report(items):
    return [{"component_id":x.component_id,"reference":x.reference,"confidence":x.confidence,"sources":list(x.sources),"conflicts":list(x.conflicts)} for x in items]
