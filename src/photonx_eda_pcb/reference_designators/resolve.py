from .model import ResolvedReference
def resolve_reference(component_id,candidates):
    items=[x for x in candidates if x.component_id==str(component_id) and x.reference]
    if not items:return ResolvedReference(str(component_id),None,0.0,(),())
    by={}
    for x in items:by.setdefault(x.reference,[]).append(x)
    ranked=sorted(by.items(),key=lambda kv:(-max(x.confidence for x in kv[1]),kv[0]))
    ref,group=ranked[0]
    return ResolvedReference(str(component_id),ref,max(x.confidence for x in group),tuple(sorted({x.source for x in group})),tuple(r for r,_ in ranked[1:]))
