def analyze_fuses(protection_candidates,identity_by_id=None):
    from .model import FuseCandidate
    identity_by_id=identity_by_id or {};out=[]
    for p in protection_candidates:
        if p.kind!="fuse":continue
        text=" ".join(str(x or "") for x in (getattr(identity_by_id.get(p.component_id),"kind",None),getattr(identity_by_id.get(p.component_id),"value",None))).lower()
        resettable=True if any(x in text for x in ("ptc","polyfuse","resettable")) else None
        out.append(FuseCandidate(p.component_id,p.protected_nets,resettable,p.confidence,tuple(p.evidence)))
    return out
