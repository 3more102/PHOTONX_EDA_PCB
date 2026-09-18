def select_entries(bundle,roles=None,suffixes=None):
    roles=set(roles or []);suffixes=tuple(suffixes or ())
    return [e for e in bundle.entries if (not roles or e.role in roles) and (not suffixes or e.path.endswith(suffixes))]
