def decode_resistor_marking(text):
    s=str(text).strip().upper()
    if s in {"0","000","0R0"}:return 0.0
    if "R" in s:
        try:return float(s.replace("R","."))
        except ValueError:return None
    if s.isdigit() and len(s)==3:
        return int(s[:2])*(10**int(s[2]))
    if s.isdigit() and len(s)==4:
        return int(s[:3])*(10**int(s[3]))
    return None
