def pdn_report(items):
    return [{"net_id":x.net_id,"nominal_voltage":x.nominal_voltage,"estimated_resistance_ohm":x.estimated_resistance_ohm,"estimated_drop_v":x.estimated_drop_v,"confidence":x.confidence,"assumptions":list(x.assumptions)} for x in items]
