def classify_excellon_command(text:str)->str:
    s=text.strip().upper()
    if s=='M48': return 'header_begin'
    if s in {'M95','%'}: return 'header_end'
    if s.startswith(('METRIC','INCH')): return 'units'
    if s.startswith('T'): return 'tool'
    if s.startswith('G85'): return 'slot'
    if s.startswith('G00') or s.startswith('G01'): return 'route'
    if ('X' in s or 'Y' in s) and not s.startswith('G'): return 'hit'
    if s in {'M30','M00'}: return 'eof'
    return 'unknown'
