_SIMPLE_ESCAPES = {
    '"': 0x22,
    "\\": 0x5C,
    "a": 0x07,
    "b": 0x08,
    "f": 0x0C,
    "n": 0x0A,
    "r": 0x0D,
    "t": 0x09,
    "v": 0x0B,
}
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
_OCTAL_DIGITS = frozenset("01234567")


def _decode_quoted(text: str, start: int) -> tuple[str, int]:
    data = bytearray()
    pos = start

    while pos < len(text):
        char = text[pos]

        if char == '"':
            try:
                value = bytes(data).decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(
                    "quoted string escape sequence does not produce valid UTF-8"
                ) from exc
            return value, pos + 1

        if char != "\\":
            data.extend(char.encode("utf-8"))
            pos += 1
            continue

        pos += 1
        if pos >= len(text):
            raise ValueError("unterminated string")

        escape = text[pos]
        pos += 1

        if escape in _SIMPLE_ESCAPES:
            data.append(_SIMPLE_ESCAPES[escape])
            continue

        if escape == "x":
            end = pos
            while (
                end < len(text)
                and end - pos < 2
                and text[end] in _HEX_DIGITS
            ):
                end += 1

            if end == pos:
                # Match KiCad DSNLEXER: a malformed \x escape becomes literal "x".
                data.extend(b"x")
            else:
                data.append(int(text[pos:end], 16))
            pos = end
            continue

        if escape in _OCTAL_DIGITS:
            end = pos
            while (
                end < len(text)
                and end - pos < 2
                and text[end] in _OCTAL_DIGITS
            ):
                end += 1
            data.append(int(escape + text[pos:end], 8))
            pos = end
            continue

        # Match KiCad DSNLEXER's fallback for an unknown escape: preserve
        # both the backslash and the escaped character.
        data.extend(b"\\")
        data.extend(escape.encode("utf-8"))

    raise ValueError("unterminated string")


def lex(text: str):
    out = []
    i = 0

    while i < len(text):
        char = text[i]

        if char.isspace():
            i += 1
            continue

        if char in "()":
            out.append(char)
            i += 1
            continue

        if char == '"':
            value, i = _decode_quoted(text, i + 1)
            out.append(("str", value))
            continue

        end = i
        while (
            end < len(text)
            and not text[end].isspace()
            and text[end] not in "()"
        ):
            end += 1

        out.append(("atom", text[i:end]))
        i = end

    return out
