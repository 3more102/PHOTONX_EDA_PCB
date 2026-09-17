import re
_RE=re.compile(r"(?:X(?P<x>-?[0-9.]+))?(?:Y(?P<y>-?[0-9.]+))?")
def parse_excellon_xy(text:str)->dict[str,str|None]:
    m=_RE.fullmatch(text.strip())
    if not m or (m['x'] is None and m['y'] is None): raise ValueError('invalid Excellon coordinate')
    return m.groupdict()
