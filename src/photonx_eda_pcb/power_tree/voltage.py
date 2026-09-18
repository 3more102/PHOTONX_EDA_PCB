import re
def parse_voltage(label):
    s=str(label or "").upper().replace(" ","")
    m=re.search(r"([+-]?\d+)V(\d+)",s)
    if m:
        sign=-1 if m.group(1).startswith("-") else 1
        whole=abs(int(m.group(1)));frac=m.group(2)
        return sign*float(f"{whole}.{frac}")
    m=re.search(r"([+-]?\d+(?:\.\d+)?)V",s)
    if m:return float(m.group(1))
    return None
