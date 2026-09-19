import re
from dataclasses import dataclass
_RE=re.compile(r"%FS(?P<zero>[LT])A?X(?P<xi>[0-9])(?P<xd>[0-9])Y(?P<yi>[0-9])(?P<yd>[0-9])\*%")
@dataclass(frozen=True)
class GerberFormatSpec:
    x_integer:int; x_decimal:int; y_integer:int; y_decimal:int; zero_suppression:str
def parse_format_spec(text:str)->GerberFormatSpec:
    m=_RE.fullmatch(text.strip())
    if not m: raise ValueError("invalid Gerber format specification")
    return GerberFormatSpec(int(m['xi']),int(m['xd']),int(m['yi']),int(m['yd']),"leading" if m['zero']=='L' else "trailing")
