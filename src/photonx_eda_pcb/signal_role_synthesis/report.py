def roles_report(items):return [{"net_id":x.net_id,"roles":list(x.roles),"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
