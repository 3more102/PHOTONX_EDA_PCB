def routing_density(stats):
    if not stats.board_width_mm or not stats.board_height_mm:return None
    area=stats.board_width_mm*stats.board_height_mm
    return None if area<=0 else round(stats.total_track_length_mm/area,8)
def component_density(stats):
    if not stats.board_width_mm or not stats.board_height_mm:return None
    area=stats.board_width_mm*stats.board_height_mm
    return None if area<=0 else round(stats.components/area,8)
