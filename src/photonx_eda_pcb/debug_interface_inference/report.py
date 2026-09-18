def debug_report(items):return [{"protocol":x.protocol,"nets":list(x.nets),"components":list(x.components),"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
