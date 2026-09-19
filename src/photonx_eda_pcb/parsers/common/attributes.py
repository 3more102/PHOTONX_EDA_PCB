from __future__ import annotations

import re


_NAME_RE = re.compile(
    r"(?:\.[_$A-Za-z][_$A-Za-z0-9]*|[_$A-Za-z][_$A-Za-z0-9]*)\Z"
)
_HEX_RE = re.compile(r"[0-9A-Fa-f]+\Z")


def _decode_attribute_field(value: str) -> str:
    """Decode Gerber Unicode escapes without accepting malformed metadata."""

    decoded: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char in "%*":
            raise ValueError(
                f"unescaped reserved Gerber character {char!r} in attribute field"
            )

        if char != "\\":
            decoded.append(char)
            index += 1
            continue

        if index + 1 >= len(value) or value[index + 1] not in {"u", "U"}:
            raise ValueError(
                "Gerber attribute backslash must begin a Unicode escape"
            )

        width = 4 if value[index + 1] == "u" else 8
        start = index + 2
        end = start + width
        digits = value[start:end]
        if len(digits) != width or _HEX_RE.fullmatch(digits) is None:
            raise ValueError(f"invalid Gerber Unicode escape at offset {index}")

        codepoint = int(digits, 16)
        if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
            raise ValueError(f"invalid Unicode scalar U+{codepoint:04X}")

        decoded.append(chr(codepoint))
        index = end

    return "".join(decoded)


def parse_attribute_fields(text: str) -> tuple[str, list[str]]:
    """Parse one Gerber TF/TA/TO/TD attribute command.

    Attribute field whitespace is data and is therefore preserved. Unicode
    escapes are decoded only after comma field boundaries are identified, so
    an escaped comma remains inside its field.

    Raises:
        ValueError: if the command wrapper, attribute name, or Unicode escape
            is malformed.
    """

    source = text.strip()
    if not source:
        raise ValueError("empty Gerber attribute")

    if source.startswith("%"):
        if not source.endswith("*%"):
            raise ValueError("Gerber attribute command must end with '*%'")
        body = source[1:-2]
    else:
        body = source[:-1] if source.endswith("*") else source

    command = body[:2] if body[:2] in {"TF", "TA", "TO", "TD"} else None
    if command is not None:
        body = body[2:]

    if command == "TD" and body == "":
        return "", []

    parts = body.split(",")
    name = parts[0]
    if _NAME_RE.fullmatch(name) is None:
        raise ValueError(f"invalid Gerber attribute name {name!r}")

    return name, [_decode_attribute_field(field) for field in parts[1:]]
