from .ast import MacroVariableDefinition
from .expression import eval_expr
from .primitives import primitive_name
from .variables import substitute


def evaluate_macro(primitives, variables=None):
    environment = {}
    defined = set()

    for key, value in (variables or {}).items():
        token = str(key)
        if token.startswith("$"):
            token = token[1:]
        if not token.isdigit() or int(token) <= 0:
            raise ValueError(f"invalid macro variable name: {key!r}")
        token = str(int(token))
        if token in defined:
            raise ValueError(f"macro variable ${token} is defined more than once")
        environment[token] = float(value)
        defined.add(token)

    out = []
    for statement in primitives:
        if isinstance(statement, MacroVariableDefinition):
            token = str(statement.index)
            if token in defined:
                raise ValueError(f"macro variable ${token} cannot be redefined")
            environment[token] = eval_expr(
                substitute(statement.expression, environment)
            )
            defined.add(token)
            continue

        values = [
            eval_expr(substitute(modifier, environment))
            for modifier in statement.modifiers
        ]
        out.append(
            {
                "code": statement.code,
                "kind": primitive_name(statement.code),
                "values": values,
            }
        )
    return out
