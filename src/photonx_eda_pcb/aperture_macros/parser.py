from .ast import MacroPrimitive
from .lexer import split_macro_statements
def parse_macro_body(body):
    result=[]
    for statement in split_macro_statements(body):
        if statement.startswith("0"): continue
        parts=[part.strip() for part in statement.split(",")]
        if not parts[0].isdigit(): raise ValueError(f"unsupported macro statement: {statement}")
        result.append(MacroPrimitive(int(parts[0]),tuple(parts[1:])))
    return result
