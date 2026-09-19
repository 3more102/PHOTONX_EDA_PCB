from __future__ import annotations

import re


_NAME_RE = re.compile(
    r"(?:\.[_$A-Za-z][_$A-Za-z0-9]*|[_$A-Za-z][_$A-Za-z0-9]*)\Z"
)
_HEX_RE = re.compile(r"[0-9A-Fa-f]+\Z")
_X2_COMMAND = re.compile(r"^%(TF|TA|TO|TD)([^*%]*)\*%$")

_FILE_STANDARD_NAMES = {
    ".Part",
    ".FileFunction",
    ".FilePolarity",
    ".SameCoordinates",
    ".CreationDate",
    ".GenerationSoftware",
    ".ProjectId",
    ".MD5",
}
_APERTURE_STANDARD_NAMES = {
    ".AperFunction",
    ".DrillTolerance",
    ".FlashText",
}
_OBJECT_STANDARD_NAMES = {
    ".N",
    ".P",
    ".C",
    ".CRot",
    ".CMfr",
    ".CMPN",
    ".CVal",
    ".CMnt",
    ".CFtp",
    ".CPgN",
    ".CPgD",
    ".CHgt",
    ".CLbN",
    ".CLbD",
    ".CSup",
}
_STANDARD_NAMES_BY_COMMAND = {
    "TF": _FILE_STANDARD_NAMES,
    "TA": _APERTURE_STANDARD_NAMES,
    "TO": _OBJECT_STANDARD_NAMES,
}
_ALL_STANDARD_NAMES = (
    _FILE_STANDARD_NAMES | _APERTURE_STANDARD_NAMES | _OBJECT_STANDARD_NAMES
)


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
            raise ValueError("Gerber attribute backslash must begin a Unicode escape")

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


def _validate_attribute_name(name: str) -> None:
    if _NAME_RE.fullmatch(name) is None:
        raise ValueError(f"invalid Gerber attribute name {name!r}")


def parse_attribute_fields(text: str) -> tuple[str, list[str]]:
    """Parse one Gerber attribute command and safely decode its value fields."""

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
    _validate_attribute_name(name)
    return name, [_decode_attribute_field(field) for field in parts[1:]]


def validate_x2_attribute_command(text: str) -> tuple[str, str, list[str]]:
    """Validate X2 command shape/domain and decode its string fields safely."""

    candidate = text.strip()
    match = _X2_COMMAND.fullmatch(candidate)
    if match is None:
        raise ValueError("expected %TF/%TA/%TO/%TD command terminated by *%")

    command, payload = match.groups()

    if command == "TD":
        if "," in payload:
            raise ValueError("TD deletes an attribute by name and cannot carry values")
        if not payload:
            return command, "", []
        name = payload
        values: list[str] = []
    else:
        if not payload:
            raise ValueError(f"{command} requires an attribute name")
        parts = payload.split(",")
        name = parts[0]
        values = [_decode_attribute_field(field) for field in parts[1:]]

    _validate_attribute_name(name)

    if name.startswith("."):
        allowed = (
            _ALL_STANDARD_NAMES
            if command == "TD"
            else _STANDARD_NAMES_BY_COMMAND[command]
        )
        if name not in allowed:
            if name in _ALL_STANDARD_NAMES:
                raise ValueError(
                    f"standard attribute {name} is not valid in the {command} domain"
                )
            raise ValueError(f"unknown reserved standard attribute {name}")

    if command == "TO" and name in {".C", ".N"} and "," not in payload:
        raise ValueError(f"TO{name} requires the comma that begins its value field")

    return command, name, values
