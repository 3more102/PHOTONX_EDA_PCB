def validate_pinout(pinout):
    issues=[];ids=set()
    for p in pinout.pins:
        if p.pin_id in ids:issues.append("PINOUT_DUPLICATE_PIN")
        ids.add(p.pin_id)
        if not 0<=p.confidence<=1:issues.append("PINOUT_CONFIDENCE_RANGE")
    return issues
