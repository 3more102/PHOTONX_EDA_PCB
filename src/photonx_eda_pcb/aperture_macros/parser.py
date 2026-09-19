import re

from .ast import MacroPrimitive, MacroVariableDefinition
from .lexer import split_macro_statements


_VARIABLE_DEFINITION = re.compile(r"^\\$(\\d+)\\s*=\\s*(.+)$")


def parse_macro_body(body):
    result = []
    for statement in split_macro_statements(body):
        if statement.startswith("0"):
            continue

        assignment = _VARIABLE_DEFINITION.fullmatch(statement)
        if assignment is not None:
            index = int(assignment.group(1))
            expression = assignment.group(2).strip()
            if index <= 0 or not expression:
                raise ValueError(f"invalid macro variable definition: {statement}")
            result.append(MacroVariableDefinition(index, expression))
            continue

        parts = [part.strip() for part in statement.split(",")]
        if not parts[0].isdigit():
            raise ValueError(f"unsupported macro statement: {statement}")
        result.append(MacroPrimitive(int(parts[0]), tuple(parts[1:])))
    return result
