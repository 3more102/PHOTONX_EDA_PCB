def pinout_report(p):return {"component_id":p.component_id,"pins":[{"pin":x.pin_id,"net":x.net_id,"role":x.role,"confidence":x.confidence,"evidence":list(x.evidence)} for x in p.pins]}
