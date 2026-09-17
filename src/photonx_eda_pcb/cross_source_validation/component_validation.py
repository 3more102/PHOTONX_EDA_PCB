def compare_component_refs(inferred,external):
    a=set(inferred); b=set(external)
    return {'missing_external':sorted(a-b),'missing_inferred':sorted(b-a),'common':sorted(a&b)}
