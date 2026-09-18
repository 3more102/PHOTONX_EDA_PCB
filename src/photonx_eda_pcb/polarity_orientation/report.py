def polarity_report(items):return [{"component_id":x.component_id,"positive_pin":x.positive_pin,"negative_pin":x.negative_pin,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
def orientation_report(items):return [{"component_id":x.component_id,"rotation_deg":x.rotation_deg,"pin1":x.pin1,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
