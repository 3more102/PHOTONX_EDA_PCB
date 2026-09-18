def instance_members(fingerprint):
    comps=tuple(n[2:] for n in fingerprint.nodes if n.startswith("C:"))
    nets=tuple(n[2:] for n in fingerprint.nodes if n.startswith("N:"))
    return comps,nets
