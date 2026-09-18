def identity_report(items):
    return [{"component_id":x.component_id,"kind":x.kind,"value":x.value,"footprint":x.footprint,"mpn":x.mpn,"confidence":x.confidence,"sources":list(x.sources),"conflicts":list(x.conflicts)} for x in items]
