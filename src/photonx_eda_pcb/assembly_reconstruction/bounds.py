def assembly_bounds(components):
    if not components:return None
    xs=[c.center[0] for c in components];ys=[c.center[1] for c in components]
    return (min(xs),min(ys),max(xs),max(ys))
