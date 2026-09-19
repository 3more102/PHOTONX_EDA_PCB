import re


_DECIMAL = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
_SIGNED_DECIMAL = rf"[+-]?{_DECIMAL}"
_EXCELLON_TOOL = re.compile(
    rf"(?m)^T[0-9]+C{_DECIMAL}(?:F{_DECIMAL})?(?:S{_DECIMAL})?\s*$"
)
_EXCELLON_COORD = re.compile(
    rf"(?m)^(?:X{_SIGNED_DECIMAL}(?:Y{_SIGNED_DECIMAL})?|"
    rf"Y{_SIGNED_DECIMAL}(?:X{_SIGNED_DECIMAL})?)\s*$"
)


def content_hints(text):
    s = str(text).lstrip("\ufeff\x00 \t\r\n")
    u = s.upper()
    out = []

    if (
        "%FS" in u
        or "%MO" in u
        or "%ADD" in u
        or "M02*" in u
        or ("G70*" in u or "G71*" in u) and "D" in u
    ):
        out.append(("gerber", .8, "gerber_commands"))

    if "M48" in u and (
        "METRIC" in u
        or "INCH" in u
        or "M71" in u
        or "M72" in u
    ):
        out.append(("excellon", .85, "excellon_header"))
    elif _EXCELLON_TOOL.search(u) and _EXCELLON_COORD.search(u):
        # Headerless drill files exist in the wild. Detection is allowed, but
        # the lexical hint must still use Excellon's ASCII numeric grammar;
        # the production parser remains authoritative for semantic validity
        # and still requires explicit units before geometry is trusted.
        out.append(("excellon", .72, "excellon_tool_coordinate_shape"))

    if "IPC-D-356" in u or s.startswith("P  "):
        out.append(("ipc356", .85, "ipc356_header"))
    if s.startswith("(kicad_pcb"):
        out.append(("kicad_pcb", .98, "kicad_root"))
    if s.startswith("(kicad_sch"):
        out.append(("kicad_schematic", .98, "kicad_root"))
    if s.startswith("{") or s.startswith("["):
        out.append(("json", .6, "json_shape"))
    return out
