def protocol_report(items):return [{"protocol":x.protocol,"nets":list(x.net_ids),"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
