import re
_RE=re.compile(r"G85X(?P<x1>-?[0-9.]+)Y(?P<y1>-?[0-9.]+)X(?P<x2>-?[0-9.]+)Y(?P<y2>-?[0-9.]+)")
def parse_slot_command(text:str)->tuple[str,str,str,str]:
    m=_RE.fullmatch(text.strip().upper())
    if not m: raise ValueError('unsupported slot command')
    return m['x1'],m['y1'],m['x2'],m['y2']
