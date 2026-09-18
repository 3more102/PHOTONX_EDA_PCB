from .normalize import reference_parts
def reference_range(refs):
    parts=[reference_parts(r) for r in refs];parts=[p for p in parts if p]
    if not parts:return None
    prefixes={p[0] for p in parts}
    return None if len(prefixes)!=1 else (next(iter(prefixes)),min(p[1] for p in parts),max(p[1] for p in parts))
