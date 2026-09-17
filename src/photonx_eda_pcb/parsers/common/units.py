def normalize_units(value:str)->str:
    v=value.strip().lower()
    if v in {"mm","metric","millimeter","millimeters"}: return "mm"
    if v in {"in","inch","inches","imperial"}: return "inch"
    raise ValueError(f"unsupported units: {value}")
def to_mm(value:float,units:str)->float: return value if normalize_units(units)=="mm" else value*25.4
