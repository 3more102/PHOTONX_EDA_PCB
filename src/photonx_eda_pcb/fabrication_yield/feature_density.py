def feature_density(metrics):
    if not metrics.board_area_mm2 or metrics.board_area_mm2<=0:return None
    return round((metrics.track_count+metrics.via_count+metrics.drill_count)/metrics.board_area_mm2,6)
