def interpolation_mode(gcode:str)->str:
    g=gcode.strip().upper().rstrip('*')
    return {'G01':'linear','G1':'linear','G02':'cw_arc','G2':'cw_arc','G03':'ccw_arc','G3':'ccw_arc'}.get(g,'unknown')
