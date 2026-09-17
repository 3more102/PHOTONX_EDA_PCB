import re
from dataclasses import dataclass
_RE=re.compile(r"%ADD(?P<code>\d+)(?P<shape>[CROP]),?(?P<a>[0-9.]+)?(?:X(?P<b>[0-9.]+))?\*%")
@dataclass(frozen=True)
class ApertureDefinition:
    code:int
    shape:str
    x:float|None
    y:float|None=None
def parse_aperture(text:str)->ApertureDefinition:
    m=_RE.fullmatch(text.strip())
    if not m: raise ValueError("unsupported aperture definition")
    return ApertureDefinition(int(m['code']),m['shape'],float(m['a']) if m['a'] else None,float(m['b']) if m['b'] else None)
