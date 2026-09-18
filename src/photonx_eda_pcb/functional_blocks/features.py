def component_feature(identity,roles=()):
    kind=str(getattr(identity,"kind","unknown") or "unknown").lower()
    return {"kind":kind,"roles":tuple(sorted(map(str,roles)))}
