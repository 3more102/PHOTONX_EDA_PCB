def content_hints(text):
    s=str(text).lstrip()
    out=[]
    if "%FS" in s or "%MO" in s or "M02*" in s:out.append(("gerber",.8,"gerber_commands"))
    if "M48" in s and ("METRIC" in s or "INCH" in s):out.append(("excellon",.8,"excellon_header"))
    if "IPC-D-356" in s or s.startswith("P  "):out.append(("ipc356",.85,"ipc356_header"))
    if s.startswith("(kicad_pcb"):out.append(("kicad_pcb",.98,"kicad_root"))
    if s.startswith("(kicad_sch"):out.append(("kicad_schematic",.98,"kicad_root"))
    if s.startswith("{") or s.startswith("["):out.append(("json",.6,"json_shape"))
    return out
