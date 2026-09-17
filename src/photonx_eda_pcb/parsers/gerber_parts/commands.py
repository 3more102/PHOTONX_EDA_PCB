def classify_command(text:str)->str:
    s=text.strip()
    if s.startswith('%FS'): return 'format'
    if s.startswith('%MO'): return 'units'
    if s.startswith('%ADD'): return 'aperture_definition'
    if s.startswith(('%TF.','%TA.','%TO.','%TD')): return 'attribute'
    if s.startswith('%LP'): return 'polarity'
    if s.startswith('%SR'): return 'step_repeat'
    if s in {'G36*','G37*'}: return 'region'
    if s.startswith('G0') or s.startswith('G1') or s.startswith('G2') or s.startswith('G3'): return 'gcode'
    if s.startswith('D') and s.endswith('*'): return 'aperture_select'
    if any(k in s for k in ('X','Y')) and s.endswith('*'): return 'coordinate'
    if s=='M02*': return 'eof'
    return 'unknown'
