from math import isfinite

from .lexer import lex


def _parse_atom(value: str):
    try:
        return int(value)
    except ValueError:
        pass

    try:
        number = float(value)
    except ValueError:
        return value

    if not isfinite(number):
        raise ValueError(f"non-finite numeric atom: {value}")
    return number


def parse_sexpr(text: str):
    toks = lex(text)
    pos = 0

    def parse_one():
        nonlocal pos
        if pos >= len(toks):
            raise ValueError("unexpected eof")

        token = toks[pos]
        pos += 1

        if token == "(":
            result = []
            while pos < len(toks) and toks[pos] != ")":
                result.append(parse_one())
            if pos >= len(toks):
                raise ValueError("missing )")
            pos += 1
            return result

        if token == ")":
            raise ValueError("unexpected )")

        kind, value = token
        if kind == "str":
            return value
        return _parse_atom(value)

    root = parse_one()
    if pos != len(toks):
        raise ValueError("trailing tokens")
    return root
