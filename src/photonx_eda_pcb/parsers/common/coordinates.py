from dataclasses import dataclass
@dataclass(frozen=True)
class CoordinateFormat:
    integer:int=2
    decimal:int=4
    zero_suppression:str="leading"
    def width(self): return self.integer+self.decimal
def parse_coordinate(raw:str,fmt:CoordinateFormat)->float:
    s=raw.strip(); neg=s.startswith('-'); s=s[1:] if neg else s
    if '.' in s: val=float(s)
    else:
        if not s.isdigit(): raise ValueError(f"invalid coordinate: {raw}")
        val=int(s)/(10**fmt.decimal)
    return -val if neg else val
