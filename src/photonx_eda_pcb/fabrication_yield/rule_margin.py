def rule_margin(value,minimum):
    if value is None:return None
    return round(float(value)-float(minimum),6)
