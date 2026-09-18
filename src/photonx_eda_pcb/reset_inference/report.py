def reset_report(items):
    return [{"net_id":x.net_id,"active_low":x.active_low,"confidence":x.confidence,"fanout":x.fanout,"evidence":list(x.evidence)} for x in items]
