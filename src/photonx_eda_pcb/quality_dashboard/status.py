def score_status(score):
    s=float(score)
    if s>=.9:return "excellent"
    if s>=.75:return "good"
    if s>=.5:return "attention"
    return "poor"
