def port_report(items):return [{"connector_id":x.connector_id,"kind":x.kind,"pins":list(x.pins),"nets":list(x.nets),"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
