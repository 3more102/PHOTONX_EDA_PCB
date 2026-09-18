import re
_PATTERNS=[("data",re.compile(r"^(?:DDR_)?DQ(\d+)$")),("strobe",re.compile(r"^(?:DDR_)?DQS([PN]?\d*)$")),("address",re.compile(r"^(?:DDR_)?A(\d+)$")),("bank",re.compile(r"^(?:DDR_)?BA(\d+)$")),("command",re.compile(r"^(?:DDR_)?(RAS|CAS|WE|CS|CKE|ODT)_?N?$")),("clock",re.compile(r"^(?:DDR_)?CK([PN]?\d*)$"))]
def classify_ddr_label(label):
    s=str(label or "").upper().replace(" ","")
    for role,rx in _PATTERNS:
        if rx.match(s):return role
    return None
