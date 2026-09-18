def variant_bom_items(bom_items,variant):
    dnp={r for r,x in variant.components.items() if not x.fitted}
    out=[]
    for item in bom_items:
        refs=tuple(r for r in item.references if r not in dnp)
        if refs:out.append(type(item)(refs,item.value,item.footprint,item.mpn,item.manufacturer,len(refs)))
    return out
