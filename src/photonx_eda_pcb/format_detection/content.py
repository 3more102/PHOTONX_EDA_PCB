import re


_EXCELLON_TOOL = re.compile(r"(?m)^T\d+C[0-9.]+(?:F[0-9.]+)?(?:S[0-9.]+)?\s*$")
_EXCELLON_COORD = re.compile(r"(?m)^(?:X[+-]?[0-9.]+)?(?:Y[+-]?[0-9.]+)?\s*$")


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
    elif _EXCELLON_TOOL.search(u) and (
        re.search(r"(?m)^X[+-]?[0-9.]+(?:Y[+-]?[0-9.]+)?\s*$", u)
        or re.search(r"(?m)^Y[+-]?[0-9.]+\s*$", u)
    ):
        # Headerless drill files exist in the wild. Detection is allowed, but
        # the parser still requires explicit units before geometry is trusted.
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
