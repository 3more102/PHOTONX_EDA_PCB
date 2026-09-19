import re


_VARIABLE = re.compile(r"\$(\d+)")


def substitute(expr, variables, undefined=0.0):
    normalized = {}
    for key, value in variables.items():
        token = str(key)
        if token.startswith("$"):
            token = token[1:]
        if not token.isdigit() or int(token) <= 0:
            raise ValueError(f"invalid macro variable name: {key!r}")
        normalized[str(int(token))] = value

    def replace(match):
        index = int(match.group(1))
        if index <= 0:
            raise ValueError("macro variable names must use a positive integer")
        return str(normalized.get(str(index), undefined))

    return _VARIABLE.sub(replace, str(expr))
