from dataclasses import dataclass
@dataclass(frozen=True)
class MacroPrimitive: code:int; modifiers:tuple[str,...]
def parse_macro_line(text:str):
    parts=[x.strip() for x in text.strip().rstrip('*').split(',')]
    if not parts or not parts[0].isascii() or not parts[0].isdigit(): raise ValueError('invalid aperture macro primitive')
    return MacroPrimitive(int(parts[0]),tuple(parts[1:]))
