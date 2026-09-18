def estimate_rail_width(panel_bounds,board_bounds):
    px0,py0,px1,py1=panel_bounds;bx0,by0,bx1,by1=board_bounds
    vals=[bx0-px0,by0-py0,px1-bx1,py1-by1]
    vals=[v for v in vals if v>=0]
    return min(vals) if vals else None
