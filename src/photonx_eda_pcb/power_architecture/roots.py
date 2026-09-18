def source_rails(architecture):
    downstream={d.downstream for d in architecture.dependencies}
    candidates=set(architecture.rails)
    return tuple(sorted(candidates-downstream))
def leaf_rails(architecture):
    upstream={d.upstream for d in architecture.dependencies}
    return tuple(sorted(set(architecture.rails)-upstream))
