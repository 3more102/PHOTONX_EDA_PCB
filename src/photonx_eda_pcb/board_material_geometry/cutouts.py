from shapely.geometry import Polygon
def cutout_polygons(board):
    from .material import outline_loops
    loops=outline_loops(board)
    if not loops:return []
    outer=loops[0];shell=Polygon(outer.exterior);out=[]
    for ring in outer.interiors:
        p=Polygon(ring)
        if not p.is_empty:out.append(p)
    for p in loops[1:]:
        if shell.contains(p.representative_point()) and not any(p.equals(q) for q in out):
            out.append(p)
    return sorted(out,key=lambda p:(-p.area,p.bounds))
