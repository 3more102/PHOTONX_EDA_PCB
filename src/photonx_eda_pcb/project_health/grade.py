def health_grade(score):
    s=float(score)
    if s>=.9:return "A"
    if s>=.8:return "B"
    if s>=.7:return "C"
    if s>=.6:return "D"
    return "F"
