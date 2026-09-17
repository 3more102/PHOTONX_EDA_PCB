from .candidate import NetNameCandidate
from .normalize import normalize_net_name
_POWER={"GND","VSS","VCC","VDD","3V3","5V","12V","VBAT"}
def candidates_from_label(net_id,label,source="explicit_label"):
    name=normalize_net_name(label)
    if not name:return []
    confidence=1.0 if source=="explicit_label" else (0.8 if name.upper() in _POWER else 0.6)
    rationale="explicit label" if source=="explicit_label" else "semantic pattern"
    return [NetNameCandidate(net_id,name,confidence,source,rationale)]
