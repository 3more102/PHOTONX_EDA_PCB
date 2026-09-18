def termination_report(items):return [{"component_id":x.component_id,"kind":x.kind,"nets":list(x.nets),"value_ohm":x.value_ohm,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
