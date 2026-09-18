def variant_matrix(variants):
    refs=sorted({r for v in variants for r in v.components})
    return {"references":refs,"variants":{v.name:{r:(v.components.get(r).fitted if r in v.components else True) for r in refs} for v in variants}}
