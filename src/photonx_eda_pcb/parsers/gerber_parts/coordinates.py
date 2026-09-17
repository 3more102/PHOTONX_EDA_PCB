import re
_RE=re.compile(r"(?:X(?P<x>-?[0-9.]+))?(?:Y(?P<y>-?[0-9.]+))?(?:I(?P<i>-?[0-9.]+))?(?:J(?P<j>-?[0-9.]+))?(?:D0?(?P<d>[123]))?\*")
def parse_xy_words(text:str)->dict[str,str|None]:
    m=_RE.fullmatch(text.strip())
    if not m: raise ValueError("invalid Gerber coordinate command")
    return m.groupdict()
