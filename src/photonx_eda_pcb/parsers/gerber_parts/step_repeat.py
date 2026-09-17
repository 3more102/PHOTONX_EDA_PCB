import re
_RE=re.compile(r"%SR(?:X(?P<x>\d+))?(?:Y(?P<y>\d+))?(?:I(?P<i>[0-9.]+))?(?:J(?P<j>[0-9.]+))?\*%")
def parse_step_repeat(text:str)->dict[str,float|int]:
    m=_RE.fullmatch(text.strip())
    if not m: raise ValueError('invalid step-repeat')
    if not any(m.groupdict().values()): return {"x":1,"y":1,"i":0.0,"j":0.0}
    return {"x":int(m['x'] or 1),"y":int(m['y'] or 1),"i":float(m['i'] or 0),"j":float(m['j'] or 0)}
