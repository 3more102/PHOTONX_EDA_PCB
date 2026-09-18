def risk_level(score):
    s=float(score)
    if s>=.75:return "high"
    if s>=.4:return "medium"
    if s>0:return "low"
    return "none"
