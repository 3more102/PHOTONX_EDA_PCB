def analyze_input_protection(connector_paths,protection_candidates):
    from .model import InputProtectionPath
    by={p.component_id:p for p in protection_candidates};out=[]
    for path in connector_paths:
        comps=[n[2:] for n in path.nodes if str(n).startswith("C:")]
        prot=[by[c] for c in comps if c in by]
        if not prot:continue
        kinds=tuple(x.kind for x in prot);score=.55+min(.3,.08*len(prot))+.1*path.confidence
        out.append(InputProtectionPath(path.connector_id,path.target_id,tuple(x.component_id for x in prot),kinds,round(min(score,1),6),("connector_path","protection_identity")))
    return out
