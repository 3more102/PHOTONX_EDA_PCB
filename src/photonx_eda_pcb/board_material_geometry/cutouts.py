def cutout_polygons(board):
    from .material import outline_loops
    loops=outline_loops(board)
    if len(loops)<2:return []
    outer=loops[0]
    return [p for p in loops[1:] if outer.contains(p.representative_point())]
