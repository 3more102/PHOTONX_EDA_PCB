import re
_VOLT=re.compile(r"(\d+)(?:V|V_)?(\d+)?")
def voltage_hint(name):
    s=str(name or "").upper().replace(".","V")
    if "GND" in s or s=="0V":return 0.0
    m=_VOLT.search(s)
    if not m:return None
    whole=float(m.group(1));frac=m.group(2)
    return whole+(float("0."+frac) if frac else 0.0)
