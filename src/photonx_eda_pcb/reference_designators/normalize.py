import re
_RX=re.compile(r"^([A-Za-z]+)([0-9]+)([A-Za-z]?)$")
def normalize_reference(ref):
    s=str(ref or "").strip().upper().replace(" ","")
    return s if _RX.match(s) else ""
def reference_parts(ref):
    m=_RX.match(normalize_reference(ref))
    return None if not m else (m.group(1),int(m.group(2)),m.group(3))
