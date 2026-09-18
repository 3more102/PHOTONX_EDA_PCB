from math import hypot
def close_component_pairs(components,min_spacing_mm=0.2):
    out=[]
    for i,a in enumerate(components):
        for b in components[i+1:]:
            if a.side!=b.side:continue
            d=hypot(a.center[0]-b.center[0],a.center[1]-b.center[1])
            if d<float(min_spacing_mm):out.append((a.reference,b.reference,d))
    return out
