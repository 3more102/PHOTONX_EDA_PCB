def peripheral_report(pmap):
    return [{"component_id":x.component_id,"protocol":x.protocol,"nets":list(x.nets),"peers":list(x.peer_components),"role":x.role,"confidence":x.confidence,"evidence":list(x.evidence)} for x in pmap.bindings]
