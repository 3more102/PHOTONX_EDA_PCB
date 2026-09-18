def split_sides(assembly):
    top=[c for c in assembly.components if c.side in {"top","front","f"}]
    bottom=[c for c in assembly.components if c.side in {"bottom","back","b"}]
    other=[c for c in assembly.components if c not in top and c not in bottom]
    return top,bottom,other
