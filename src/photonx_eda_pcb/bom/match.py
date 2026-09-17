def match_component(component,bom_index):
    reference=getattr(component,"reference",None)
    return bom_index.get(reference) if reference else None
