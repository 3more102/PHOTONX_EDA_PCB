def channel_report(items):return [{"id":x.id,"instances":list(x.instances),"kind":x.kind,"confidence":x.confidence,"evidence":list(x.evidence),"differences":list(x.differences)} for x in items]
