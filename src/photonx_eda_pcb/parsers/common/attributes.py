from __future__ import annotations

import re


_NAME = re.compile(r"^(?:\.[_A-Za-z$][_A-Za-z0-9]*|[_A-Za-z$][_A-Za-z0-9]*)$")
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


def parse_attribute_fields(text: str) -> tuple[str, list[str]]:
    body = text.strip().strip("%").rstrip("*")
    if body.startswith(("TF.", "TA.", "TO.", "TD")):
        body = body[2:] if body.startswith("TD") else body[3:]
    parts = [part.strip() for part in body.split(",")]
    return parts[0], parts[1:]


def validate_x2_attribute_command(text: str) -> tuple[str, str, list[str]]:
    """Validate the Gerber 2026.05 X2 attribute command grammar.

    This validates command shape, attribute-name grammar, standard-name domain,
    and TD's no-value rule. Attribute-specific value semantics remain the
    responsibility of the production handlers that consume those attributes.
    """

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
        values = parts[1:]

    if _NAME.fullmatch(name) is None:
        raise ValueError(f"invalid attribute name {name!r}")

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

    # The 2026.05 grammar gives .C an explicit comma lookahead so it cannot
    # be confused with .CRot and related component attributes.
    if command == "TO" and name == ".C" and "," not in payload:
        raise ValueError("TO.C requires the comma that begins its value field")

    return command, name, values
