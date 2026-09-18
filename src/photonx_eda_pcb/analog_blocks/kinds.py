def component_kind(identity):
    return str(getattr(identity,"kind","unknown") or "unknown").lower()
def is_kind(identity,*tokens):
    k=component_kind(identity)
    return any(t.lower() in k for t in tokens)
