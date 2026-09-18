def apply_variant(components,variant):
    by={str(getattr(c,"reference","")):c for c in components}
    fitted=[];dnp=[]
    for ref,c in by.items():
        rule=variant.components.get(ref)
        if rule is not None and not rule.fitted:dnp.append(c)
        else:fitted.append(c)
    return fitted,dnp
