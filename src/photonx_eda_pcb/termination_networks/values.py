def parse_resistance(value):
    if value is None:return None
    s=str(value).strip().upper().replace("Ω","").replace("OHM","")
    mult=1.0
    if s.endswith("K"):mult=1e3;s=s[:-1]
    elif s.endswith("M"):mult=1e6;s=s[:-1]
    if "R" in s:s=s.replace("R",".")
    try:return float(s)*mult
    except ValueError:return None
