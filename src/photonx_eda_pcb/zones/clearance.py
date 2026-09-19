def effective_clearance(zone,board_default_mm=0.2):
    if zone.clearance_mm is None:return float(board_default_mm)
    return max(float(zone.clearance_mm),float(board_default_mm))

def clearance_violation(distance_mm,zone,board_default_mm=0.2):
    return distance_mm < effective_clearance(zone,board_default_mm)
