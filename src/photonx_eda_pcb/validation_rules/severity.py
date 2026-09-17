ERROR='error'
WARNING='warning'
INFO='info'
VALID={ERROR,WARNING,INFO}
def normalize_severity(value:str)->str:
    v=value.lower().strip()
    if v not in VALID: raise ValueError(f'unknown severity {value}')
    return v
