def mcu_interface_report(items):
    return [{"component_id":x.component_id,"protocol":x.protocol,"nets":list(x.nets),"pins":[list(p) for p in x.pins],"peers":list(x.peers),"confidence":x.confidence} for x in items]
