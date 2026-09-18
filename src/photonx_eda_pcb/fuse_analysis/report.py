def fuse_report(items):return [{"component_id":x.component_id,"nets":list(x.nets),"resettable":x.resettable,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
