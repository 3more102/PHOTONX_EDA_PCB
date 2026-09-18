def variant_summary(v):
    return {"name":v.name,"explicit_components":len(v.components),"dnp":sorted(r for r,x in v.components.items() if not x.fitted)}
