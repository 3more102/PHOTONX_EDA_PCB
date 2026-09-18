from shapely.geometry import LineString
from shapely.ops import unary_union,polygonize

def outline_loops(board):
    lines=[LineString([(s.start.x,s.start.y),(s.end.x,s.end.y)]) for s in board.outline]
    if not lines:return []
    return sorted(list(polygonize(unary_union(lines))),key=lambda p:(-p.area,p.bounds))

def board_material_shape(board):
    polys=outline_loops(board)
    if not polys:return None
    outer=polys[0]
    material=outer
    for p in polys[1:]:
        rp=p.representative_point()
        if outer.contains(rp):
            # If the chosen outer polygon already excludes this region,
            # representative-point containment is false and we do not subtract twice.
            material=material.difference(p)
    return material
