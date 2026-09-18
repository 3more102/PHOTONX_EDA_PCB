def clock_report(items):
    return [{"net_id":x.net_id,"confidence":x.confidence,"fanout":x.fanout,"frequency_hz":x.frequency_hz,"evidence":list(x.evidence)} for x in items]
