from .slots import is_canned_slot
def classify_excellon_command(text:str)->str:
    s=text.strip().upper()
    if s=="M48":return "header_begin"
    if s in {"M95","%"}:return "header_end"
    if s.startswith(("METRIC","INCH")):return "units"
    if s.startswith("T"):return "tool"
    if "G85" in s and is_canned_slot(s):return "slot"
    if s.startswith(("G00","G01","G02","G03")):return "route"
    if ("X" in s or "Y" in s) and not s.startswith("G") and "G85" not in s:return "hit"
    if s in {"M30","M00"}:return "eof"
    return "unknown"
