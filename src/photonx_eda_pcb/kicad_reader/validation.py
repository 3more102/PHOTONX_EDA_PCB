def validate_board_dict(data):
    issues=[]
    if not data.get("edge_lines"):issues.append(("warning","KICAD_EDGE_MISSING"))
    codes=[n["code"] for n in data.get("nets",())]
    if len(codes)!=len(set(codes)):issues.append(("error","KICAD_DUP_NET_CODE"))
    for fp in data.get("footprints",()):
        for pad in fp.get("pads",()):
            if pad.get("drill_shape")=="oval":
                size=pad.get("drill_size")
                if not size or min(size)<=0:issues.append(("error","KICAD_OVAL_DRILL_INVALID"))
    return issues
