def validate_supply_domain(d):
    issues=[]
    if not d.name:issues.append("SUPPLY_DOMAIN_NAME_EMPTY")
    if not 0<=d.confidence<=1:issues.append("SUPPLY_DOMAIN_CONFIDENCE_RANGE")
    if d.voltage is not None and d.voltage<0:issues.append("SUPPLY_DOMAIN_NEGATIVE_VOLTAGE")
    return issues
