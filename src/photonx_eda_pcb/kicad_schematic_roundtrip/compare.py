from .canonical import canonical_schematic
def compare_schematics(a,b):
    ca,cb=canonical_schematic(a),canonical_schematic(b);diff=[]
    for key in sorted(set(ca)|set(cb)):
        if ca.get(key)!=cb.get(key):diff.append(key)
    return diff
