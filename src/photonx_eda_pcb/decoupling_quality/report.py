def decoupling_report(items):return [{"component_id":x.component_id,"power_net":x.power_net,"score":x.score,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
