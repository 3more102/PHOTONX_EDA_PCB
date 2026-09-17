import re
from dataclasses import dataclass
_RE=re.compile(r"%FS(?P<zero>[LT])A?X(?P<xi>\d)(?P<xd>\d)Y(?P<yi>\d)(?P<yd>\d)\*%")
@dataclass(frozen=True)
class GerberFormatSpec:
    x_integer:int; x_decimal:int; y_integer:int; y_decimal:int; zero_suppression:str
def parse_format_spec(text:str)->GerberFormatSpec:
    m=_RE.fullmatch(text.strip())
    if not m: raise ValueError("invalid Gerber format specification")
    return GerberFormatSpec(int(m['xi']),int(m['xd']),int(m['yi']),int(m['yd']),"leading" if m['zero']=='L' else "trailing")
