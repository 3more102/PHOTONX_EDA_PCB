def total_known_thickness_mm(stackup): return sum(x.thickness_mm or 0.0 for x in stackup.layers)
def unknown_thickness_layers(stackup): return [x.name for x in stackup.layers if x.thickness_mm is None]
