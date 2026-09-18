def risk_level(value):
    v=float(value)
    if v>=.75:return "high"
    if v>=.45:return "medium"
    if v>=.2:return "low"
    return "minimal"
