def block_report(items):return [{"id":b.id,"kind":b.kind,"components":list(b.components),"nets":list(b.nets),"confidence":b.confidence,"evidence":list(b.evidence)} for b in items]
