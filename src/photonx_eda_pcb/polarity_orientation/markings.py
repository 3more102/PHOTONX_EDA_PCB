def marking_polarity(marking):
    s=str(marking or "").upper().strip()
    if s in {"+","POS","ANODE"}:return "positive"
    if s in {"-","NEG","CATHODE","K"}:return "negative"
    return None
