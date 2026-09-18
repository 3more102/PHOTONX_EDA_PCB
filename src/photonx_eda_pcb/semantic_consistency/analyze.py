from .model import SemanticFinding,SemanticConsistencyReport
def analyze_semantic_consistency(identities=(),references=(),net_names=(),pin_functions=()):
    out=[];ref_seen={}
    for r in references:
        if r.reference:
            if r.reference in ref_seen and ref_seen[r.reference]!=r.component_id:
                out.append(SemanticFinding("REFERENCE_DUPLICATE","error",r.component_id,f"{r.reference} also assigned to {ref_seen[r.reference]}"))
            ref_seen[r.reference]=r.component_id
        if r.conflicts:out.append(SemanticFinding("REFERENCE_CONFLICT","warning",r.component_id,",".join(r.conflicts)))
    for x in identities:
        if x.conflicts:out.append(SemanticFinding("IDENTITY_CONFLICT","warning",x.component_id,",".join(x.conflicts)))
        if x.kind is None:out.append(SemanticFinding("IDENTITY_UNRESOLVED","info",x.component_id,"component kind unresolved"))
    for n in net_names:
        if n.conflicts:out.append(SemanticFinding("NET_NAME_CONFLICT","warning",n.net_id,",".join(n.conflicts)))
    for p in pin_functions:
        if p.conflicts:out.append(SemanticFinding("PIN_FUNCTION_CONFLICT","warning",f"{p.connector_id}:{p.pin}",",".join(p.conflicts)))
        if p.function is None:out.append(SemanticFinding("PIN_FUNCTION_UNRESOLVED","info",f"{p.connector_id}:{p.pin}","function unresolved"))
    return SemanticConsistencyReport(sorted(out,key=lambda x:(x.severity,x.code,x.object_id)))
