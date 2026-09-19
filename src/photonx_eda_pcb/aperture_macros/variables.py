import re


_VARIABLE = re.compile(r"\\$(\\d+)")


def substitute(expr, variables):
    normalized = {
        str(key)[1:] if str(key).startswith("$") else str(key): value
        for key, value in variables.items()
    }

    def replace(match):
        key = match.group(1)
        if key not in normalized:
            return match.group(0)
        return str(normalized[key])

    return _VARIABLE.sub(replace, str(expr))
