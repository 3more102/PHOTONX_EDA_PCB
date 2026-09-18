from .normalize import normalize_reference
def index_bom(records):
    out={}
    for r in records:
        key=normalize_reference(r.reference)
        if key in out:raise ValueError(f"duplicate BOM reference {key}")
        out[key]=r
    return out
