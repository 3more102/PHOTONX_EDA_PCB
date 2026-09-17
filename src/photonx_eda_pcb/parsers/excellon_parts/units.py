def parse_excellon_units(text:str)->dict[str,str]:
    s=text.strip().upper()
    if s.startswith('METRIC'): units='mm'
    elif s.startswith('INCH'): units='inch'
    else: raise ValueError('unsupported Excellon units statement')
    zero='leading' if 'LZ' in s else ('trailing' if 'TZ' in s else 'unspecified')
    return {"units":units,"zero_suppression":zero}
