def infer_emc_components(protection_candidates):
    from .model import EmcCandidate
    return [EmcCandidate(p.component_id,p.kind,p.protected_nets,p.confidence,p.evidence) for p in protection_candidates if p.kind in {"ferrite","common_mode_choke"}]
