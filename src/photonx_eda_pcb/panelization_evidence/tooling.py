def tooling_hole_score(holes,edge_margin_mm=8.0):
    return min(1.0,len(list(holes))/3.0)
