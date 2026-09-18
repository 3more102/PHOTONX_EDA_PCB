PREFIX_KIND={"R":"resistor","C":"capacitor","L":"inductor","D":"diode","LED":"led","J":"connector","U":"ic","Q":"transistor"}
def infer_kind_from_reference(reference):
    s=str(reference).upper()
    for p in sorted(PREFIX_KIND,key=len,reverse=True):
        if s.startswith(p):return PREFIX_KIND[p]
    return None
