import re
from decimal import Decimal

def _scaled_decimal(number, multiplier):
    return float(Decimal(number) * Decimal(multiplier))

def parse_resistance(value):
    if value is None:return None
    s=str(value).strip().upper().replace("Ω","").replace("OHM","").replace(" ","")
    m=re.fullmatch(r"(\d+(?:\.\d+)?)([KMG]?)",s)
    if not m:return None
    mult={"":"1","K":"1e3","M":"1e6","G":"1e9"}[m.group(2)]
    return _scaled_decimal(m.group(1),mult)

def parse_capacitance(value):
    if value is None:return None
    s=str(value).strip().upper().replace("F","").replace("µ","U").replace(" ","")
    m=re.fullmatch(r"(\d+(?:\.\d+)?)([PNU]?)",s)
    if not m:return None
    mult={"":"1","P":"1e-12","N":"1e-9","U":"1e-6"}[m.group(2)]
    return _scaled_decimal(m.group(1),mult)

def parse_inductance(value):
    if value is None:return None
    s=str(value).strip().upper().replace("H","").replace("µ","U").replace(" ","")
    m=re.fullmatch(r"(\d+(?:\.\d+)?)([NUM]?)",s)
    if not m:return None
    mult={"":"1","N":"1e-9","U":"1e-6","M":"1e-3"}[m.group(2)]
    return _scaled_decimal(m.group(1),mult)
