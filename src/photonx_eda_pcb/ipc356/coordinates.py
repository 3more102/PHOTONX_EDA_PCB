def parse_coord(value,scale=1000.0):
    if value is None:return None
    text=str(value).strip()
    sign=-1.0 if text.startswith("-") else 1.0
    digits=text.lstrip("+-")
    if not digits.isdigit(): raise ValueError(f"invalid IPC-356 coordinate: {value}")
    return sign*int(digits)/scale
