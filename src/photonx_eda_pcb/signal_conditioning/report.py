def conditioning_report(items):return [{"id":x.id,"kind":x.kind,"components":list(x.components),"nets":list(x.nets),"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
