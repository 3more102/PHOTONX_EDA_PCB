import re
_PATTERNS=(re.compile(r"^(.*?)[_\[]?(\d+)\]?$"),)
def split_indexed_label(label):
    s=str(label or "").strip().upper()
    for rx in _PATTERNS:
        m=rx.match(s)
        if m and m.group(1):
            base=m.group(1).rstrip("_")
            return base,int(m.group(2))
    return None
