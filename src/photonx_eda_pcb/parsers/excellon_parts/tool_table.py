import re
from dataclasses import dataclass
_RE=re.compile(r"T(?P<tool>\d+)(?:C(?P<diam>[0-9.]+))?")
@dataclass(frozen=True)
class DrillTool:
    number:int
    diameter:float|None=None
def parse_tool_definition(text:str)->DrillTool:
    m=_RE.fullmatch(text.strip())
    if not m: raise ValueError('invalid tool definition')
    return DrillTool(int(m['tool']),float(m['diam']) if m['diam'] else None)
